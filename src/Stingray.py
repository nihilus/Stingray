import collections
import idautils
import logging
import idaapi
import idc
import os

class Config( object ):

    PLUGIN_NAME         = "Stingray"
    PLUGIN_COMMENT      = "find strings in current function recursively"
    PLUGIN_HELP         = "www.github.com/darx0r/Stingray"
    PLUGIN_HOTKEY       = "Shift-S"
    CONFIG_FILE_PATH    = os.path.join( idc.GetIdaDirectory(), 
                                        "cfg/Stingray.cfg" )

    CHOOSER_TITLE           = "Stingray - Function Strings"
    CHOOSER_COLUMN_NAMES    = [ "Xref", "Address",  "Type", "String"    ]
    CHOOSER_COLUMN_SIZES    = [ 18,     8,          5,      80          ]
    CHOOSER_COLUMNS         = [ list(c) for c in 
                                zip(CHOOSER_COLUMN_NAMES, CHOOSER_COLUMN_SIZES) ]
    CHOOSER_ROW             = collections.namedtuple(   "ResultRow", 
                                                        CHOOSER_COLUMN_NAMES )

    PLUGIN_TEST                = False
    SEARCH_RECURSION_MAXLVL    = 0
    
    MENU_CONTEXT = None

    # Icon in PNG format
    PLUGIN_ICON_PNG =    (
        "\x89\x50\x4E\x47\x0D\x0A\x1A\x0A\x00\x00\x00\x0D\x49\x48\x44\x52"
        "\x00\x00\x00\x10\x00\x00\x00\x10\x08\x04\x00\x00\x00\xB5\xFA\x37"
        "\xEA\x00\x00\x00\x02\x62\x4B\x47\x44\x00\xFF\x87\x8F\xCC\xBF\x00"
        "\x00\x00\x09\x70\x48\x59\x73\x00\x00\x00\x48\x00\x00\x00\x48\x00"
        "\x46\xC9\x6B\x3E\x00\x00\x00\xC4\x49\x44\x41\x54\x28\xCF\xBD\x91"
        "\x3D\x0B\x81\x61\x14\x86\xAF\xE7\xF5\xCA\x77\xCA\x20\x0B\x61\xA0"
        "\x58\x8C\x06\x65\xF4\x11\x99\x8C\xDE\x92\x18\x64\xF6\x13\xFC\x03"
        "\x25\x59\xEC\x7E\x80\x32\xDB\x2C\x36\x61\x92\x85\x59\x49\xD4\xE3"
        "\xF1\x35\x48\x8C\xCE\x5D\x67\x39\xD7\xE9\xDC\xE7\x1C\xF8\x4B\xB8"
        "\xF1\xFD\x06\x8A\xD4\xBE\xD6\x4C\xB7\xD4\x61\x46\xE2\xA3\x64\xC6"
        "\x4B\x8C\x00\x08\x86\x48\xE6\xD4\x49\x13\xA5\x80\x41\x86\xBC\x52"
        "\x8E\x2C\x71\x2C\x37\xB6\xAD\x00\xC9\x85\x03\x5B\x8E\x0C\x08\x12"
        "\x56\xAE\xEC\xAA\xF5\x1E\x42\x33\xF4\x93\x90\xBC\xD4\x47\x7B\x9F"
        "\x55\xA2\x2B\xF6\x56\xA9\xBD\x80\x0D\xA9\x77\xC0\x85\x8D\x8A\x98"
        "\x30\x62\xC5\xF9\x8E\x2C\x69\x12\x79\x8E\x70\x3C\x20\x8F\x92\x4E"
        "\x88\xAA\x32\x3C\x65\xCD\x8E\x05\x63\x7A\xB4\x28\x7F\xEE\xED\xC6"
        "\xAF\x96\x2E\xA8\xDB\x34\x48\xE2\xFC\xC3\xA3\xAE\x2A\xB7\x2E\x12"
        "\xA0\x06\x96\xA7\x00\x00\x00\x25\x74\x45\x58\x74\x64\x61\x74\x65"
        "\x3A\x63\x72\x65\x61\x74\x65\x00\x32\x30\x31\x35\x2D\x31\x30\x2D"
        "\x30\x31\x54\x31\x31\x3A\x35\x34\x3A\x33\x38\x2D\x30\x35\x3A\x30"
        "\x30\x9E\x3D\x6C\xB8\x00\x00\x00\x25\x74\x45\x58\x74\x64\x61\x74"
        "\x65\x3A\x6D\x6F\x64\x69\x66\x79\x00\x32\x30\x31\x35\x2D\x31\x30"
        "\x2D\x30\x31\x54\x31\x31\x3A\x35\x34\x3A\x33\x38\x2D\x30\x35\x3A"
        "\x30\x30\xEF\x60\xD4\x04\x00\x00\x00\x00\x49\x45\x4E\x44\xAE\x42"
        "\x60\x82"        )


    @staticmethod
    def init():

        NO_HOTKEY = ""
        SETMENU_INS = 0
        NO_ARGS = tuple()

        menu = idaapi.add_menu_item(    "Options/", 
                                        "{} Config".format(Config.PLUGIN_NAME), 
                                        NO_HOTKEY, 
                                        SETMENU_INS, 
                                        Config.stingray_config, 
                                        NO_ARGS )
        if menu is None:
            del menu
        
        Config.MENU_CONTEXT = menu
        Config.load()


    @staticmethod
    def destory():

        if Config.MENU_CONTEXT:
            idaapi.del_menu_item(Config.MENU_CONTEXT)
        
        try:
            Config.save()
        except IOError:
            logging.getLogger("Stingray").warning("Failed to write config file")


    @staticmethod
    def load():

        try:
            maxlvl = int( open(Config.CONFIG_FILE_PATH,"rb").read() )
            Config.SEARCH_RECURSION_MAXLVL = maxlvl
        except:
            pass


    @staticmethod
    def save():

        config_data = str(Config.SEARCH_RECURSION_MAXLVL)
        open(Config.CONFIG_FILE_PATH,"wb").write(config_data)


    @staticmethod
    def stingray_config():

        input = idc.AskLong(    Config.SEARCH_RECURSION_MAXLVL, 
                                "Please enter string search max. depth:"
                                "\n( 0 - non-recursive mode )"            )

        if input >= 0:
            Config.SEARCH_RECURSION_MAXLVL = input


# ------------------------------------------------------------------------------


class StringParsingException( Exception ):
    pass


class String( object ):

    ASCSTR = [  "C",
                "Pascal",
                "LEN2",
                "Unicode",
                "LEN4",
                "ULEN2",    
                "ULEN4"    ]


    def __init__( self, xref, addr ):

        type = idc.GetStringType(addr)
        if type < 0 or type >= len(String.ASCSTR):
            raise StringParsingException()

        CALC_MAX_LEN = -1
        string = str( idc.GetString(addr, CALC_MAX_LEN, type) )

        self.xref = xref
        self.addr = addr
        self.type = type
        self.string = string


    def get_row( self ):

        xref = "{}:{:08X}".format(GetFunctionName(self.xref), self.xref)
        addr = "{:08X}".format(self.addr)
        type = String.ASCSTR[self.type]
        string = self.string
        # IDA Chooser doesn't like tuples ... row should be a list
        return list( Config.CHOOSER_ROW(xref, addr, type, string) )


def find_function_strings( func_ea ):

    end_ea = idc.FindFuncEnd(func_ea)
    if end_ea == idaapi.BADADDR: return

    strings = []
    for line in idautils.Heads(func_ea, end_ea):
        refs = idautils.DataRefsFrom(line)
        for ref in refs:
            try:
                strings.append( String(line, ref) )
            except StringParsingException:
                continue

    return strings


def find_function_callees( func_ea, maxlvl ):

    callees = []
    visited = set()
    pending = set( (func_ea,) )
    lvl = 0

    while len(pending) > 0:
        func_ea = pending.pop()
        visited.add(func_ea)

        func_name = GetFunctionName(func_ea)
        if not func_name: continue
        callees.append(func_ea)

        func_end = FindFuncEnd(func_ea)
        if func_end == BADADDR: continue

        lvl +=1
        if lvl >= maxlvl: continue
        
        all_refs = set()
        for line in Heads(func_ea, func_end):

            if not isCode( GetFlags(line) ): continue

            ALL_XREFS = 0
            refs = CodeRefsFrom(line, ALL_XREFS)
            refs = set( filter( lambda x: not (x >= func_ea and x <= func_end), 
                                refs) )
            all_refs |= refs

        all_refs -= visited
        pending |= all_refs

    return callees


class StringFinder( object ):

    def __init__( self ):
        pass


    def get_current_function_strings( self ):

        addr_in_func = idc.ScreenEA()
        curr_func = idc.GetFunctionName(addr_in_func)

        funcs = [ addr_in_func ]
        if Config.SEARCH_RECURSION_MAXLVL > 0:
            funcs = find_function_callees(  addr_in_func, 
                                            Config.SEARCH_RECURSION_MAXLVL  )

        total_strs = []
        for func in funcs:
            strs = find_function_strings(func)
            total_strs += [ s.get_row() for s in strs ]

        return total_strs


# ------------------------------------------------------------------------------


class PluginChooser( idaapi.Choose2 ):

    def __init__( self, title, columns, items, icon, embedded=False ):

        idaapi.Choose2.__init__(self, title, columns, embedded=embedded)
        self.items = items
        self.icon = icon


    def GetItems( self ):
        return self.items


    def SetItems( self, items ):
        self.items = [] if items is None else items
        self.Refresh()


    def OnClose( self ):
        pass


    def OnGetLine( self, n ):
        return self.items[n]


    def OnGetSize( self ):
        return len(self.items)


    def OnSelectLine( self, n ):

        row = Config.CHOOSER_ROW( *self.items[n] )
        xref = row.Xref.split(':')[-1]
        idc.Jump( int(xref, 16) )


# ------------------------------------------------------------------------------    


class StingrayPlugin( idaapi.plugin_t ):

    flags           = 0
    comment         = Config.PLUGIN_COMMENT
    help            = Config.PLUGIN_HELP
    wanted_name     = Config.PLUGIN_NAME
    wanted_hotkey   = Config.PLUGIN_HOTKEY

    def __init__(self, *args, **kwargs):
        super(StingrayPlugin, self).__init__(*args, **kwargs)
        self._chooser = None


    def init( self ):

        self.icon_id = idaapi.load_custom_icon( data = Config.PLUGIN_ICON_PNG, 
                                                format = "png"    )
        if self.icon_id == 0:
            raise RuntimeError("Failed to load icon data!")

        self.finder = StringFinder()

        Config.init()

        return idaapi.PLUGIN_KEEP


    def run( self, arg=0 ):

        try:
            rows = self.finder.get_current_function_strings()
            if self._chooser is None:
                self._chooser = PluginChooser(  Config.CHOOSER_TITLE, 
                                                Config.CHOOSER_COLUMNS, 
                                                rows, 
                                                self.icon_id    )
            else:
                self._chooser.SetItems(rows)
            self._chooser.Show()
        except Exception as e:
            logging.getLogger("Stingray").warning("exception", exc_info=True)
        return


    def term( self ):

        Config.destory()

        if self.icon_id != 0:
            idaapi.free_custom_icon(self.icon_id)


# ------------------------------------------------------------------------------    


def PLUGIN_ENTRY():
    return StingrayPlugin()


# ------------------------------------------------------------------------------


if Config.PLUGIN_TEST:
    print "{} - test".format(Config.PLUGIN_NAME)
    p = StingrayPlugin()
    p.init()
    p.run()
    p.term()

