#!/usr/bin/env python3

"""
Redirector2 by  b4dpxl
Based on Redireector by @random_robbie: https://github.com/random-robbie/redirector
"""

import argparse
import os
import sys
import textwrap

from http.server import HTTPServer, BaseHTTPRequestHandler


class Redirect(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def _log(self):
        if self.server.quiet:
            self.server.printer.ok(self.requestline)
        else:
            self.server.printer.info("Connection from {}:{}".format(self.client_address[0],self.client_address[1]))
            self.server.printer.ok("{}\n{}\n".format(self.requestline, str(self.headers)))

    def _log_with_body(self):
        if not self.server.quiet:
            self.server.printer.info("Connection from {}:{}".format(self.client_address[0],self.client_address[1]))
            try:
                content_length = int(self.headers.get('Content-Length', 0)) # <--- Gets the size of data
            except:
                content_length = None
            if content_length:
                post_data = self.rfile.read(content_length) # <--- Gets the data itself
                self.server.printer.ok("{}\n{}{}\n".format(
                    self.requestline,
                    str(self.headers), 
                    post_data.decode('utf-8')
                ))
                return

            else:
                self.server.printer.warn("No 'Content-Length' received")

        self._log()


    def _send_redirect(self):
        redirect_url = self.server.ssrf_url
        if self.server.expand:
            if redirect_url.endswith('/'):
                redirect_url = redirect_url[:-1]
            redirect_url += self.path
        self.server.printer.debug("Redirecting with {} to {}".format(self.server.redirect_code, redirect_url))

        self.send_response(self.server.redirect_code)
        self.send_header('Location', redirect_url)
        self.end_headers()

    def do_GET(self):
        self._log()
        self._send_redirect()


    def do_HEAD(self):
        self._log()
        self._send_redirect()

    def do_POST(self):
        self._log_with_body()
        self._send_redirect()

    def do_PUT(self):
        self._log_with_body()
        self._send_redirect()

    def do_DELETE(self):
        self._log()
        self._send_redirect()

    def do_PATCH(self):
        self._log_with_body()
        self._send_redirect()

    def do_OPTIONS(self):
        self._log()
        self._send_redirect()

    def log_message(self, format, *args):
        # suppress default access logs
        return


class RedirectHTTPServer(HTTPServer):

    def __init__(self, printer, args, server_address, RequestHandlerClass=Redirect, bind_and_activate=True):
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        self.printer = printer
        self.ssrf_url = args.ssrf_url
        self.redirect_code = args.redirect_code
        self.quiet = args.quiet
        self.expand = args.expand


class Printer:
    DEBUG = '\033[90m'
    PURPLE = '\033[95m'
    INFO = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    __debug_on = False
    __trace_on = False

    def __init__(self, debug=True, trace=False):
        self.__debug_on = debug
        self.__trace_on = trace

    def ok(self, msg):
        self.print_col("[+]", msg, self.OKGREEN)

    def info(self, msg):
        self.print_col("[*]", msg, self.INFO)

    def warn(self, msg):
        self.print_col("[~]", msg, self.WARNING)

    def error(self, msg):
        self.print_col("[!]", msg, self.FAIL)

    def debug(self, msg):
        if self.__debug_on:
            self.print_col("[-]", msg, self.DEBUG)

    def trace(self, msg):
        if self.__trace_on:
            self.__default("[ ] {}".format(msg))

    def print_col(self, msg1, msg2, col):
        print("{}{}{} {}".format(col, msg1, self.ENDC, "\n    ".join(msg2.splitlines())))

    def __default(self, msg):
        print("\n    ".join(line.splitlines()))


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-u', '--url',
        dest='ssrf_url',
        required=True,
        help='url to redirect to',
    )
    parser.add_argument(
        '-c', '--code',
        dest='redirect_code',
        required=False,
        default='302',
        help='HTTP Status Code',
        type=int
    )
    parser.add_argument(
        '-p', '--port',
        dest='port',
        required=False,
        default='5555',
        help='Port to listen to',
        type=int
    )
    parser.add_argument(
        '-q', '--quiet',
        dest='quiet',
        required=False,
        action='store_true',
        help='Supress full request logging',
        default=False
    )
    parser.add_argument(
        '-e', '--expand',
        dest='expand',
        required=False,
        action='store_true',
        help='Expand redirect URL with the path of the original request',
        default=False
    )
    parser.add_argument(
        '-v', '--verbose', 
        dest='verbose', 
        help='Verbose output', 
        required=False, 
        action='store_true'
        )
    args = parser.parse_args()

    printer = Printer(debug=args.verbose)
        
    try:
        ip = os.popen("dig +short myip.opendns.com @resolver1.opendns.com").read()
        ip = ip.replace("\n","")
        printer.info("Server Started on http://{}:{}".format(ip, args.port))
        RedirectHTTPServer(printer, args, ('', args.port)).serve_forever()

    except KeyboardInterrupt:
        sys.exit(1)


main()
