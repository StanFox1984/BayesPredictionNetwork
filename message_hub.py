#!/usr/bin/python

from datetime import date

class message_hub:
    def __init__(self):
        self.mbox = { }
        self.user_hashes = { }

    def __getattr__(self, method):
        if '_' in str(method):
            name = str(method).split('extract_')[1]
        else:
            name = str(method)
        self.add_extract_method(name)
#        print (method)
        return self.__dict__[method]

    def add_extract_method(self, name):
        construct_str = "def extract_" + name + "(s): return s['" + name + "'][0]"
#        print (construct_str)
        exec (construct_str)
#        print ("self.__dict__['extract_" + name + "'] = extract_" + name)
        exec ("self.__dict__['extract_" + name + "'] = extract_" + name)
#        print (self.__dict__)

    def handle_request(self, s):
        err_str = ""
        if not "id" in s:
            err_str = "Can't communicate without id!"
            print (err_str)
            return err_str

        _id = self.extract_id(s)

        if "register" in s:
            if _id in self.user_hashes:
                err_str = "Such user " + _id + " already registered!"
                print (err_str)
                return err_str
            if not "pass" in s:
                err_str = "No password added!"
                print (err_str)
                return err_str
            self.user_hashes[_id] = self.extract_pass(s)

        if not _id in self.user_hashes:
            err_str = "Unregistered user " + _id + "!"
            print (err_str)
            return err_str

        if not "hash" in s:
            err_str = "Couldn't authenticate without hash!"
            print (err_str)
            return err_str

        _hash = self.extract_hash(s)
        if _hash != self.user_hashes[_id]:
            err_str = "Wrong hash - not authenticating!"
            print (err_str)
            return err_str

        if "change_hash" in s:
            if not "new_hash" in s:
                err_str = "No new hash specified!"
                print (err_str)
                return err_str
            new_hash = self.extract_new_hash(s)
            self.user_hashes[_id] = new_hash

        if "send" in s:
                if not "message" in s:
                    err_str = "No message field specified!"
                    print (err_str)
                    return err_str
                message = self.extract_message(s)

                if not "to" in s:
                    err_str = "No 'to' field specified!"
                    print (err_str)
                    return err_str
                to = self.extract_to(s)

                if not to in self.user_hashes:
                    err_str = "No such recipient!"
                    print (err_str)
                    return err_str

                if not to in self.mbox:
                    self.mbox[to] = ""

                self.mbox[to] += "Date: " + date.today().strftime("%B %d, %Y") + "|To: " + to + "|From: " + _id + "|Message: " + message + "|\n"

        if "recv" in s:
            return self.mbox[_id]


def test():
    hub = message_hub()

    hub.handle_request({ "register" : "", "id" : "Stan", "pass" : "blabla", "hash" : "blabla" })

    # cause no id error
    hub.handle_request({ })

    # cause already registered error
    hub.handle_request({ "register" : "", "id" : "Stan"})

    # cause no password specified error
    hub.handle_request({ "register" : "", "id" : "Stan2"})

    # cause no such id error
    hub.handle_request({ "id" : "Stan2"})

    # cause no hash error
    hub.handle_request({ "id" : "Stan", "send" : "", "message" : "Hello World!", "to" : "Stan2" })

    # cause wrong hash error
    hub.handle_request({ "id" : "Stan", "send" : "", "message" : "Hello World!", "to" : "Stan2", "hash" : "blah" })

    # cause no such recipient error
    hub.handle_request({ "id" : "Stan", "send" : "", "message" : "Hello World!", "to" : "Stan2", "hash" : "blabla" })

    # cause no new hash error
    hub.handle_request({ "id" : "Stan", "hash" : "blabla", "change_hash" : "" })

    hub.handle_request({ "id" : "Stan", "hash" : "blabla", "change_hash" : "", "new_hash" : "blah" })

    hub.handle_request({ "register" : "", "id" : "Stan2", "pass" : "blabla", "hash" : "blabla" })

    hub.handle_request({ "id" : "Stan", "send" : "", "message" : "Hello World!", "to" : "Stan2", "hash" : "blah" })

    hub.handle_request({ "id" : "Stan", "send" : "", "message" : "Hello World2!", "to" : "Stan2", "hash" : "blah" })

    # cause again no hash error
    hub.handle_request( { "id" : "Stan2", "recv" : "" })

    # cause again wrong hash error
    hub.handle_request( { "id" : "Stan2", "recv" : "", "hash" : "bbb" })

    # should be "From: Stan Message: Hello World!"
    print (hub.handle_request( { "id" : "Stan2", "recv" : "", "hash" : "blabla" }))

