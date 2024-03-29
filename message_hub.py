#!/usr/bin/python

from datetime import date

class message_hub:
    tested = False

    def __init__(self):
        self.mbox = { }
        self.user_hashes = { }
        self.outbox = { }
        self.user_hashes["stan"] = "blah"
        self.user_locations = { }
        if message_hub.tested != True:
            message_hub.tested = True
            res = test(type(self))
            if res != True:
                print ("Self tests failed!")
            else:
                print ("Self tests passed!")

    def __getattr__(self, method):
        if 'extract_' in str(method):
            name = str(method).split('extract_')[1]
        else:
            name = str(method)
        self.add_extract_method(name)
#        print (method)
        return self.__dict__[method]

    def __getstate__(self):
        new_dict = { }
        for key in self.__dict__:
            if not "extract" in key and not "tested" in key:
                new_dict[key] = self.__dict__[key]
        return new_dict

    def __setstate__(self, d): self.__dict__.update(d)

    def add_extract_method(self, name):
        construct_str = "def extract_" + name + "(s): return s['" + name + "'][0] if type(s['" + name + "']) == list else s['" + name + "']"
#        print (construct_str)
        exec (construct_str)
#        print ("self.__dict__['extract_" + name + "'] = extract_" + name)
        exec ("self.__dict__['extract_" + name + "'] = extract_" + name)
#        print (self.__dict__)

    def authenticate_as_admin(self, s):
        if not "id" in s:
            return False

        _id = self.extract_id(s)

        if _id != "stan":
            return False

        if not _id in self.user_hashes:
            return False

        if not "hash" in s:
            return False

        _hash = self.extract_hash(s)
        if _hash != self.user_hashes[_id]:
            return False

        return True

    def handle_request(self, s):
        err_str = ""
        handled = False

        if not "id" in s:
            err_str = "Can't communicate without id!"
            print (err_str)
            return err_str

        _id = self.extract_id(s)

        if "register" in s:
            handled = True
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
            err_str = "Unregistered user, registering then :) User:" + _id + "!"
            if not "hash" in s:
                err_str += "\n No password added!"
                print (err_str)
                return err_str
            self.user_hashes[_id] = self.extract_hash(s)
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
            handled = True
            if not "new_hash" in s:
                err_str = "No new hash specified!"
                print (err_str)
                return err_str
            new_hash = self.extract_new_hash(s)
            self.user_hashes[_id] = new_hash

        if "send" in s or "sendall" in s:
            handled = True
            sendall = "sendall" in s

            if not "message" in s:
                err_str = "No message field specified!"
                print (err_str)
                return err_str
            message = self.extract_message(s)

            if len(message) > 512:
                err_str = "Message too long!"
                print (err_str)
                return err_str

            message = message.replace("%","")
            message = message.replace("\\","")
            message = message.replace("&","")
            message = message.replace("?","")

            if not "to" in s and not sendall:
                err_str = "No 'to' field specified!"
                print (err_str)
                return err_str

            if "to" in s:
                to = self.extract_to(s)

#            if not to in self.user_hashes:
#                err_str = "No such recipient!"
#                print (err_str)
#                return err_str

            if (not to in self.mbox and not sendall) or (len(str(self.mbox[to])) > 1024):
                self.mbox[to] = ""

            if (not _id in self.outbox) or (len(str(self.outbox[_id])) > 1024):
                self.outbox[_id] = ""

            if not sendall:
                msg = "Date: " + date.today().strftime("%B %d, %Y") + "|To: " + to + "|From: " + _id + "|Message: " + message + "|\n"
            else:
                msg = "Date: " + date.today().strftime("%B %d, %Y") + "|To: " + "Sent to all" + "|From: " + _id + "|Message: " + message + "|\n"

            if not sendall:
                self.mbox[to] += msg
            else:
                for to in self.mbox:
                    self.mbox[to] += msg

            self.outbox[_id] += msg

        if "recv" in s:
            handled = True
            if _id in self.mbox:
                return self.mbox[_id]
            err_str = "Mailbox is empty!"
            print (err_str)
            return err_str

        if "sent" in s:
            handled = True
            if _id in self.outbox:
                return self.outbox[_id]
            err_str = "Outbox is empty!"
            print (err_str)
            return err_str

        if "clear" in s:
            handled = True
            if _id in self.mbox:
                self.mbox[_id] = ""
            if _id in self.outbox:
                self.outbox[_id] = ""

        if "set_location" in s:
            handled = True
            location = self.extract_set_location(s)
            self.user_locations[_id] = location

        if "get_location" in s:
            handled = True
            if not "name" in s:
                err_str = "No name in request!"
                print (err_str)
                return err_str

            name = self.extract_name(s)

            if not name in self.user_locations:
                err_str = "Unknown user " + name + "!"
                print (err_str)
                return err_str

            return self.user_locations[name]

        do_clear_all = ("clearall" in s and _id == "stan") or (len(str(self.outbox)) > 8192) or (len(str(self.mbox)) > 8192)

        if do_clear_all:
            handled = True
            self.mbox = {}
            self.outbox = {}

        if not handled:
            err_str = "Unknown command! " + s
            print(err_str)
            return err_str

        return "Success!"


def test(_hubtype):
    hub = _hubtype()

    res = hub.handle_request({ "register" : "", "id" : "Stan", "pass" : "blabla", "hash" : "blabla" })

    if res != "Success!":
        return False

    # cause no id error
    res = hub.handle_request({ })
    if res != "Can't communicate without id!":
        return False

    # cause already registered error
    res = hub.handle_request({ "register" : "", "id" : "Stan"})
    if not "already registered!" in res:
        return False

    # cause no password specified error
    res = hub.handle_request({ "register" : "", "id" : "Stan2"})
    if res != "No password added!":
        return False

    # cause no such id error
    res = hub.handle_request({ "id" : "Stan2"})
    if not "Unregistered user" in res:
        return False

    # cause no hash error
    res = hub.handle_request({ "id" : "Stan", "send" : "", "message" : "Hello World!", "to" : "Stan2" })
    if res != "Couldn't authenticate without hash!":
        return False

    # cause wrong hash error
    res = hub.handle_request({ "id" : "Stan", "send" : "", "message" : "Hello World!", "to" : "Stan2", "hash" : "blah" })
    if res != "Wrong hash - not authenticating!":
        return False

    # cause no such recipient error
    res = hub.handle_request({ "id" : "Stan", "send" : "", "message" : "Hello World!", "to" : "Stan2", "hash" : "blabla" })
    if res != "No such recipient!":
        return False

    # cause no new hash error
    res = hub.handle_request({ "id" : "Stan", "hash" : "blabla", "change_hash" : "" })
    if res != "No new hash specified!":
        return False

    res = hub.handle_request({ "id" : "Stan", "hash" : "blabla", "change_hash" : "", "new_hash" : "blah" })
    if res != "Success!":
        return False

    res = hub.handle_request({ "register" : "", "id" : "Stan2", "pass" : "blabla", "hash" : "blabla" })
    if res != "Success!":
        return False

    res = hub.handle_request({ "id" : "Stan", "send" : "", "message" : "Hello World!", "to" : "Stan2", "hash" : "blah" })
    if res != "Success!":
        return False

    res = hub.handle_request({ "id" : "Stan", "send" : "", "message" : "Hello World2!", "to" : "Stan2", "hash" : "blah" })
    if res != "Success!":
        return False

    # cause again no hash error
    res = hub.handle_request( { "id" : "Stan2", "recv" : "" })
    if res != "Couldn't authenticate without hash!":
        return False

    # cause again wrong hash error
    res = hub.handle_request( { "id" : "Stan2", "recv" : "", "hash" : "bbb" })
    if res != "Wrong hash - not authenticating!":
        return False

    # should be "From: Stan Message: Hello World!"
    res = hub.handle_request( { "id" : "Stan2", "recv" : "", "hash" : "blabla" })
    if not "From: Stan|Message: Hello World!|" in res:
        return False

    return True