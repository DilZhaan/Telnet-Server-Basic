# ====================================================================
# 1. අවශ්‍ය 'Tools' (Librares/Modules) ටික import කර ගමු.
# ====================================================================

# socket module එක: මේක තමයි අපේ server එක හදන්න ප්‍රධානම දේ. මේකෙන් තමයි network එක හරහා data යවන්න/ගන්න පුළුවන් වෙන්නේ.
import socket
# threading module එක: අපේ server එකට එකපාර කීප දෙනෙක් connect වුණොත්, හැමෝටම වෙන වෙනම සේවය දෙන්න පුළුවන් වෙන්නේ මේකෙන්. හරියට 'වෙනම වැඩපොළවල්' වගේ.
import threading
# os module එක: Operating System එකේ (Windows/Mac/Linux) files, folders වගේ දේවල් එක්ක වැඩ කරන්න මේක ඕන වෙනවා.
import os
# sys module එක: මේකෙන් අපේ Python program එක කොහොමද දුවන්නේ (run වෙන්නේ) කියන එක ගැන control කරන්න පුළුවන්.
import sys
# pathlib module එකේ Path class එක: මේකෙන් files/folders වල paths (මාර්ග) හසුරුවන්න හරිම ලේසියි, ආරක්ෂිතයි.
from pathlib import Path

# ====================================================================
# 2. ප්‍රධාන Server Class එක (Server එක හදන්න Blueprint එක)
# ====================================================================

"""
මේක තමයි අපේ File Telnet Server එක හදන්න පාවිච්චි කරන Blueprint එක, නැත්නම් Class එක.

Class එකක ප්‍රධාන කොටස් දෙකක් තියෙනවා:
1.  Properties (ගුණාංග): මේවා තමයි server එකට අයිති data ටික (උදා: port එක, root directory එක).
2.  Methods (ක්‍රමවේද): මේවා තමයි server එකට කරන්න පුළුවන් වැඩ ටික (උදා: client කෙනෙක්ව handle කරන විදිය, ls command එක වැඩ කරන විදිය).

💡 මේකේ මූලික අදහස:
අපිට අවශ්‍ය වෙන්නේ Telnet (සරල text-based communication) පාවිච්චි කරලා, ආරක්ෂිතව තෝරපු folder එකක තියෙන files/folders බලන්න විතරයි. ඒ folder එකෙන් පිට කිසිම දෙයක් බලන්න බැහැ!
"""

# FileTelnetServer කියන්නේ අපේ server එකේ 'සැලැස්ම' (Class).
class FileTelnetServer:
    # මේක තමයි Constructor Method එක. Server එක start කරනකොටම මේක මුලින්ම run වෙනවා.
    def __init__(self, host='localhost', port=2323, root_dir=None):
        # host: server එක listen කරන්න ඕන IP address එක. 'localhost' කියන්නේ මේ computer එකමයි. (Property)
        self.host = host
        # port: server එක listen කරන port number එක (අංකිත 'දොරටුව'). (Property)
        self.port = port
        # root_dir: අපිට client ලාට පෙන්නන්න පුළුවන් files/folders තියෙන ඉහළම folder එක. (Property)
        # දීලා නැත්නම්, දැනට මේ program එක තියෙන folder එක root එක විදියට ගන්නවා.
        self.root_dir = Path(root_dir or os.getcwd()).resolve()
        # server_socket: network communication වලට පාවිච්චි කරන socket එක. (Property)
        self.server_socket = None
        # running: server එක on ද off ද කියලා කියන boolean (True/False) value එක. (Property)
        self.running = False
        
        # root directory එක ඇත්තටම තියෙනවද කියලා check කරනවා.
        if not self.root_dir.exists():
            # නැත්නම්, program එක නවත්තලා Error එකක් දෙනවා.
            raise ValueError(f"Root directory does not exist: {self.root_dir}")
        
        # server එකේ root directory එක මොකක්ද කියලා console එකේ print කරනවා.
        print(f"Server root directory: {self.root_dir}")

    # is_safe_path Method එක: path එක root directory එක ඇතුළේමද කියලා බලනවා.
    def is_safe_path(self, path):
        """path එක අපේ server එකේ root folder එකෙන් පිටතට යනවද කියලා check කරන Method එක."""
        try:
            # දීපු path එක absolute path එකක් බවට හරවනවා.
            resolved_path = Path(path).resolve()
            # ඒ path එක root_dir එක ඇතුළේමද කියලා check කරනවා. එහෙමනම් True දෙනවා.
            return resolved_path.is_relative_to(self.root_dir)
        # path එකක් හරවද්දී error එකක් ආවොත්,
        except (OSError, ValueError):
            # ආරක්ෂිත නැහැ කියලා False දෙනවා.
            return False

    # get_safe_path Method එක: client කෙනෙක් ඉල්ලන path එක හදලා, ඒක ආරක්ෂිතද කියලා check කරනවා.
    def get_safe_path(self, current_dir, target_path):
        """Client ඉන්න folder එක අනුව, ඉල්ලන path එක හදලා, ඒක ආරක්ෂිත නම් ආපහු දෙනවා."""
        # path එක '/' වලින් පටන් ගන්නේ නම් (root එකේ ඉඳන් path එකක්)
        if target_path.startswith('/'):
            # root එකට සාපේක්ෂව path එක හදනවා. (මුලින් තියෙන '/' එක අයින් කරලා)
            new_path = self.root_dir / target_path.lstrip('/')
        # නැත්නම් (දැනට ඉන්න folder එකට සාපේක්ෂව path එකක්)
        else:
            # දැනට ඉන්න folder එකට ඉල්ලන path එක එකතු කරනවා.
            new_path = current_dir / target_path
        
        try:
            # හදාගත්තු path එක absolute path එකක් බවට හරවනවා.
            resolved_path = new_path.resolve()
            # ඒක ආරක්ෂිතද (safe) කියලා බලනවා.
            if self.is_safe_path(resolved_path):
                # ආරක්ෂිත නම් ඒ path එක ආපහු දෙනවා.
                return resolved_path
        # error එකක් ආවොත්,
        except (OSError, ValueError):
            pass
        # ආරක්ෂිත නැත්නම් හෝ error එකක් ආවොත් None දෙනවා.
        return None

    # handle_ls_command Method එක: 'ls' (List) command එක කරන වැඩේ.
    def handle_ls_command(self, current_dir, args):
        """ls command එක process කරලා, folder එකක contents (අන්තර්ගතය) list කරලා දෙනවා."""
        try:
            target_dir = current_dir
            if args:
                # ඉල්ලපු path එක ආරක්ෂිත path එකක් බවට හරවගන්නවා.
                target_path = self.get_safe_path(current_dir, args[0])
                # ඒක folder එකක් නම්,
                if target_path and target_path.is_dir():
                    target_dir = target_path
                # ඒක file එකක් නම්,
                elif target_path and target_path.is_file():
                    # file නම විතරක් ආපහු දෙනවා.
                    return f"{target_path.name}\r\n"
                # වෙනත් දෙයක් නම් (file/folder එකක් නැත්නම්),
                else:
                    return f"ls: cannot access '{args[0]}': No such file or directory\r\n"
            
            items = []
            try:
                # target folder එක ඇතුළේ තියෙන හැම file/folder එකක්ම බලනවා.
                for item in sorted(target_dir.iterdir()):
                    # folder එකක් නම්,
                    if item.is_dir():
                        # නම අගට '/' එකක් දාලා ලැයිස්තුවට එකතු කරනවා.
                        items.append(f"{item.name}/")
                    # file එකක් නම්,
                    else:
                        # file එකේ size එක (ප්‍රමාණය) ගන්නවා.
                        size = item.stat().st_size
                        # නමයි size එකයි ලැයිස්තුවට එකතු කරනවා.
                        items.append(f"{item.name} ({size} bytes)")
                
                # ලැයිස්තුවේ මොනවා හරි තියෙනවා නම්,
                if items:
                    # හැම item එකක්ම අලුත් line එකකින් වෙන් කරලා response එක දෙනවා.
                    return "\r\n".join(items) + "\r\n"
                # folder එක හිස් නම්,
                else:
                    return "Empty directory\r\n"
            # folder එක බලන්න Permission නැත්නම්,
            except PermissionError:
                return f"ls: permission denied: {target_dir}\r\n"
                
        # වෙනත් error එකක් ආවොත්,
        except Exception as e:
            return f"ls: error: {str(e)}\r\n"

    # handle_cd_command Method එක: 'cd' (Change Directory) command එක කරන වැඩේ.
    def handle_cd_command(self, current_dir, args):
        """cd command එක process කරලා, client ගේ current directory එක change කරනවා."""
        # argument එකක් දීලා නැත්නම් ('cd' විතරක් ගැහුවොත්),
        if not args:
            # root directory එකට යනවා.
            return self.root_dir, f"Changed to root directory: {self.root_dir.relative_to(self.root_dir)}\r\n"
        
        # ඉල්ලපු path එක ආරක්ෂිත path එකක් බවට හරවගන්නවා.
        target_path = self.get_safe_path(current_dir, args[0])
        
        # path එක safe නැත්නම්,
        if not target_path:
            return current_dir, f"cd: path not allowed or invalid: {args[0]}\r\n"
        
        # path එකේ file/folder එකක් නැත්නම්,
        if not target_path.exists():
            return current_dir, f"cd: no such file or directory: {args[0]}\r\n"
        
        # ඒක directory එකක් නොවේ නම්,
        if not target_path.is_dir():
            return current_dir, f"cd: not a directory: {args[0]}\r\n"
        
        try:
            # directory එක ඇතුළට access කරන්න පුළුවන්ද කියලා බලනවා.
            list(target_path.iterdir())
            # root එකට සාපේක්ෂව අලුත් path එක හදාගන්නවා.
            relative_path = target_path.relative_to(self.root_dir)
            # අලුත් directory එකයි, සාර්ථක පණිවිඩයයි ආපහු දෙනවා.
            return target_path, f"Changed directory to: /{relative_path}\r\n"
        # access කරන්න බැරි නම් (PermissionError),
        except PermissionError:
            return current_dir, f"cd: permission denied: {args[0]}\r\n"
        # වෙනත් error එකක් ආවොත්,
        except Exception as e:
            return current_dir, f"cd: error: {str(e)}\r\n"

    # handle_cat_command Method එක: 'cat' (Concatenate/View) command එක කරන වැඩේ.
    def handle_cat_command(self, current_dir, args):
        """cat command එක process කරලා, file එකක contents (අන්තර්ගතය) පෙන්වනවා."""
        # file නමක් දීලා නැත්නම්,
        if not args:
            return "cat: missing file operand\r\n"
        
        # ඉල්ලපු file path එක ආරක්ෂිත path එකක් බවට හරවගන්නවා.
        target_path = self.get_safe_path(current_dir, args[0])
        
        if not target_path:
            return f"cat: path not allowed or invalid: {args[0]}\r\n"
        
        if not target_path.exists():
            return f"cat: {args[0]}: No such file or directory\r\n"
        
        # ඒක file එකක් නොවේ නම් (directory එකක් නම්),
        if not target_path.is_file():
            return f"cat: {args[0]}: Is a directory\r\n"
        
        try:
            # file එකේ size එක (ප්‍රමාණය) ගන්නවා.
            file_size = target_path.stat().st_size
            # size එක 1MB (Megabyte) වඩා වැඩියි නම්,
            if file_size > 1024 * 1024:
                # Error එකක් දෙනවා. (විශාල files කියවීමෙන් server එක protect කරන්න)
                return f"cat: {args[0]}: File too large (max 1MB)\r\n"
            
            # text file එකක් විදියට කියවන්න උත්සාහ කරනවා.
            try:
                # file එක කියවීම සඳහා open කරනවා.
                with open(target_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                # contents ටික ආපහු දෙනවා.
                return content + "\r\n"
            # text file එකක් විදියට කියවන්න බැරි වුණොත් (Binary File එකක් නම්),
            except UnicodeDecodeError:
                # binary විදියට (bytes විදියට) file එක open කරනවා.
                with open(target_path, 'rb') as f:
                    # මුල්ම bytes 256 විතරක් කියවනවා.
                    data = f.read(256)
                # bytes ටික Hex format එකට (00, a2, 1f වගේ) හරවනවා.
                hex_data = ' '.join(f'{b:02x}' for b in data)
                # binary file එකේ hex contents ටික පෙන්වනවා.
                return f"Binary file (showing first 256 bytes as hex):\r\n{hex_data}\r\n"
                
        # අවසර නැත්නම්,
        except PermissionError:
            return f"cat: {args[0]}: Permission denied\r\n"
        # වෙනත් error එකක් ආවොත්,
        except Exception as e:
            return f"cat: error reading {args[0]}: {str(e)}\r\n"

    # handle_pwd_command Method එක: 'pwd' (Print Working Directory) command එක කරන වැඩේ.
    def handle_pwd_command(self, current_dir):
        """pwd command එක process කරලා, client ඉන්න current directory එකේ path එක දෙනවා."""
        try:
            # root එකට සාපේක්ෂව (relative to root) path එක හදනවා.
            relative_path = current_dir.relative_to(self.root_dir)
            # path එක ආපහු දෙනවා.
            return f"/{relative_path}\r\n"
        # root directory එකේම නම්,
        except ValueError:
            return "/\r\n"

    # handle_help_command Method එක: 'help' command එක කරන වැඩේ.
    def handle_help_command(self):
        """help command එක process කරලා, available commands ලැයිස්තුවක් පෙන්වනවා."""
        help_text = """
Available commands:
  ls [path]     - List directory contents (folder එකක contents බලන්න)
  cd [path]     - Change directory (folder එකක් මාරු කරන්න)
  cat <file>    - Display file contents (file එකක contents බලන්න)
  pwd           - Show current directory (දැනට ඉන්න folder එකේ path එක බලන්න)
  help          - Show this help message (මේ help message එක බලන්න)
  quit/exit     - Disconnect from server (server එකෙන් disconnect වෙන්න)

Notes:
- All paths are relative to the server's root directory (හැම path එකක්ම server එකේ root folder එකට සාපේක්ෂයි)
- You cannot access files outside the allowed directory (root folder එකෙන් පිට කිසිම file එකක් බලන්න බැහැ)
- Binary files will show hex representation (binary files වලට hex code පෙන්වනවා)
- File size limit for 'cat' is 1MB ('cat' කරන්න පුළුවන් උපරිම file size එක 1MB)
        """
        # දෙපැත්තේ හිස්තැන් අයින් කරලා response එක දෙනවා.
        return help_text.strip() + "\r\n"

    # process_command Method එක: client දෙන හැම command එකක්ම analyze කරලා, අදාළ Method එකට යවනවා.
    def process_command(self, current_dir, command_line):
        """Client ගෙන් එන විධානය (command) process කරලා, අලුත් directory එකයි response එකයි දෙනවා."""
        command_line = command_line.strip()
        if not command_line:
            return current_dir, ""
        
        # command line එක හිස්තැන් වලින් කඩලා, command එකයි arguments ටිකයි වෙන් කරගන්නවා.
        parts = command_line.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # command එක මොකක්ද කියලා බලලා, අදාළ Method එක call කරනවා.
        if command == 'ls':
            return current_dir, self.handle_ls_command(current_dir, args)
        elif command == 'cd':
            # cd command එකෙන් directory එක වෙනස් වෙන නිසා, අලුත් directory එක ගන්නවා.
            return self.handle_cd_command(current_dir, args)
        elif command == 'cat':
            return current_dir, self.handle_cat_command(current_dir, args)
        elif command == 'pwd':
            return current_dir, self.handle_pwd_command(current_dir)
        elif command == 'help':
            return current_dir, self.handle_help_command()
        elif command in ['quit', 'exit']:
            # quit/exit command වලදී, "quit" කියන special response එක දෙනවා.
            return current_dir, "quit"
        else:
            # නොදන්නා command එකක් නම්, error message එකක් දෙනවා.
            return current_dir, f"Unknown command: {command}. Type 'help' for available commands.\r\n"

    # handle_client Method එක: server එකට connect වෙන එක client කෙනෙක්ව handle කරන වැඩේ.
    def handle_client(self, client_socket, client_address):
        """Client කෙනෙක් connect වුණාම ඒ client ගෙන් එන commands අරගෙන, response යවන Method එක."""
        print(f"Connection from {client_address}")
        # client ගේ current directory එක root එක විදියට set කරනවා.
        current_dir = self.root_dir
        
        try:
            # client ට Welcome Message එක යවනවා.
            welcome_msg = f"""Welcome to File Telnet Server!
Connected to: {self.root_dir}
Type 'help' for available commands.
Current directory: /

file_server> """
            # message එක encode කරලා client ට යවනවා.
            client_socket.send(welcome_msg.encode('utf-8'))
            
            # client ගෙන් එන data තියාගන්න Buffer එකක්.
            buffer = ""
            # server එක දුවන තාක් කල්,
            while self.running:
                try:
                    # client ගෙන් data recv (ගන්නවා) කරනවා.
                    data = client_socket.recv(1024)
                    # data නැත්නම්, client disconnect වෙලා කියලා තේරුම් අරගෙන break වෙනවා.
                    if not data:
                        break
                    
                    # ලැබුණු data, buffer එකට decode කරලා එකතු කරනවා.
                    buffer += data.decode('utf-8')
                    
                    # buffer එකේ අලුත් line එකක් (new command එකක්) තියෙන තාක් කල්,
                    while '\n' in buffer:
                        # line එකයි, ඉතිරි buffer එකයි වෙන් කරගන්නවා.
                        line, buffer = buffer.split('\n', 1)
                        # line එකේ අග තියෙන 'carriage return' අයින් කරනවා.
                        line = line.rstrip('\r')
                        
                        # line එකේ command එකක් තියෙනවා නම්,
                        if line.strip():
                            # command එක process කරනවා.
                            current_dir, response = self.process_command(current_dir, line)
                            
                            # response එක "quit" නම්,
                            if response == "quit":
                                client_socket.send(b"Goodbye!\r\n")
                                return # client connection එක close කරලා එළියට යනවා.
                            
                            # response එකක් තියෙනවා නම්,
                            if response:
                                client_socket.send(response.encode('utf-8'))
                        
                        # command එක ඉවර වුණාට පස්සේ Prompt එකක් (file_server> වගේ) යවනවා.
                        try:
                            # root එකට සාපේක්ෂව path එක අරගෙන prompt එක හදනවා.
                            rel_path = current_dir.relative_to(self.root_dir)
                            prompt = f"/{rel_path} > "
                        except ValueError:
                            prompt = "/ > "
                        
                        client_socket.send(prompt.encode('utf-8'))
                        
                # socket එකේ timeout එකක් ආවොත්,
                except socket.timeout:
                    continue
                # data decode කරද්දී error එකක් ආවොත්,
                except UnicodeDecodeError:
                    client_socket.send(b"Error: Invalid character encoding\r\n")
                    continue
                    
        # client handle කරද්දී වෙනත් error එකක් ආවොත්,
        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
        # කෙසේ වෙතත්, අවසානයේදී,
        finally:
            try:
                # client socket එක close කරනවා.
                client_socket.close()
            except:
                pass
            print(f"Connection closed: {client_address}")

    # start Method එක: server එක start කරන වැඩේ.
    def start(self):
        """Server එක start කරලා, clients ලා එනකම් listen කරන Method එක."""
        try:
            # TCP/IP socket එකක් හදනවා.
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # socket එක නැවත පාවිච්චි කරන්න අවසර දෙනවා (re-use address).
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # host:port එකට socket එක bind කරනවා.
            self.server_socket.bind((self.host, self.port))
            # clients ලාට connect වෙන්න listen කරන්න පටන් ගන්නවා.
            self.server_socket.listen(5)
            # server එක running බව සලකුණු කරනවා.
            self.running = True
            
            print(f"File Telnet Server listening on {self.host}:{self.port}")
            print(f"Root directory: {self.root_dir}")
            print("Press Ctrl+C to stop the server")
            
            # server එක දුවන තාක් කල්,
            while self.running:
                try:
                    # අලුත් client කෙනෙක් එනකම් accept (බලන් ඉන්නවා) කරනවා.
                    client_socket, client_address = self.server_socket.accept()
                    # client socket එකට timeout එකක් දානවා (විනාඩි 5).
                    client_socket.settimeout(300)
                    
                    # හැම client කෙනෙක්ම වෙනම Thread එකකින් handle කරන්න පටන් ගන්නවා.
                    client_thread = threading.Thread(
                        target=self.handle_client, 
                        args=(client_socket, client_address)
                    )
                    # ප්‍රධාන program එක නැවතුනොත් මේ thread එකත් නවතින්න සලකුණු කරනවා (Daemon Thread).
                    client_thread.daemon = True
                    # client thread එක start කරනවා.
                    client_thread.start()
                    
                # socket error එකක් ආවොත්,
                except socket.error as e:
                    if self.running:
                        print(f"Socket error: {e}")
                    
        # program එක නවත්වන්න Ctrl+C එබුවොත්,
        except KeyboardInterrupt:
            print("\nShutting down server...")
        # වෙනත් error එකක් ආවොත්,
        except Exception as e:
            print(f"Server error: {e}")
        # කෙසේ වෙතත්, අවසානයේදී,
        finally:
            self.stop() # server එක නවත්වන Method එක call කරනවා.

    # stop Method එක: server එක නවත්වන වැඩේ.
    def stop(self):
        """Server එක නවත්වන Method එක."""
        # running state එක False කරනවා.
        self.running = False
        if self.server_socket:
            try:
                # server socket එක close කරනවා.
                self.server_socket.close()
            except:
                pass

# ====================================================================
# 3. Main Program Function එක
# ====================================================================

# main function එක: program එක මුලින්ම run වෙන්නේ මෙතනින්.
def main():
    # program එක පටන් ගන්නකොට දීපු arguments (අගයන්) බලනවා.
    if len(sys.argv) > 1:
        # පළවෙනි argument එක root directory එක විදියට ගන්නවා.
        root_directory = sys.argv[1]
    else:
        # argument එකක් දීලා නැත්නම්, path එක enter කරන්න කියලා client ගෙන් අහනවා.
        root_directory = input("Enter the root directory path (or press Enter for current directory): ").strip()
        # හිස් නම්, මේ program එක තියෙන folder එකම ගන්නවා.
        if not root_directory:
            root_directory = os.getcwd()
    
    # directory එක තියෙනවද කියලා බලනවා.
    if not os.path.exists(root_directory):
        print(f"Error: Directory '{root_directory}' does not exist!")
        return # program එක නවත්වනවා.
    
    # ඒක folder එකක්ද කියලා බලනවා.
    if not os.path.isdir(root_directory):
        print(f"Error: '{root_directory}' is not a directory!")
        return # program එක නවත්වනවා.
    
    try:
        # server object එක හදලා,
        server = FileTelnetServer(root_dir=root_directory)
        # server එක start කරනවා.
        server.start()
    # server එක start කරද්දී error එකක් ආවොත්,
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Failed to start server: {e}")

# මේ file එක direct run කළොත්, main() function එක call කරනවා.
if __name__ == "__main__":
    main()