# File Notifier - AI Coding Agent Instructions

## Project Overview
**File Notifier** is a PyQt6-based Windows desktop application that monitors specified folders for file downloads and sends system notifications when files complete downloading. It runs as a system tray application in the background.

## Architecture & Data Flow

### Core Components
1. **[main.py](../main.py)** - PyQt6 GUI with system tray integration
   - `MainWindow`: Main application window managing UI state, folder configuration, and monitoring lifecycle
   - Loads/saves monitoring folders to `config.json`
   - Spawns `FolderMonitorWorker` in separate QThread to prevent UI blocking

2. **[utils/monitor.py](../utils/monitor.py)** - File system monitoring worker
   - `FolderMonitorWorker`: QThread worker emitting log signals to GUI
   - `MonitorHandler`: Watchdog event handler detecting file completion via file extensions
   - Detection strategy: Filters temp extensions (`.tmp`, `.crdownload`, `.part`, etc.) to distinguish final files from in-progress downloads

### Threading Model
- **Main thread**: GUI operations (PyQt6 widgets, config file I/O)
- **Monitor thread**: Blocks in `run()` loop checking `self.running` flag; observers call callbacks asynchronously
- **Signal path**: `FolderMonitorWorker.log_signal` → `MainWindow.add_log()` (thread-safe PyQt6 signal)

## Developer Workflows

### Building Standalone Executable
```bash
pyinstaller main.spec
# or
pyinstaller NotificadorDeDescargas.spec
```
Outputs `.exe` in `dist/` directory. The `.spec` files configure PyQt6 hooks and icon embedding.

### Running the Application
```bash
python main.py
```
Loads `config.json` on startup; if missing, creates empty config with no monitored folders.

### Testing
- [test.py](../test.py) - Main test file (purpose TBD from project)
- [utils/test.py](../utils/test.py) - Monitor module tests
- Run with: `pytest` or `python test.py`

## Key Conventions & Patterns

### Configuration Management
- **Storage**: `config.json` (UTF-8 JSON format) with `{"folders": [...]}` structure
- **Pattern**: Load on startup → modify in-memory → save on config change
- **Error handling**: Missing file defaults to empty config; exceptions logged to UI

### Event Detection Logic
File is considered "downloaded" when:
1. File created/moved event detected → check file extension
2. Extension NOT in `TEMP_EXT` list AND filename doesn't start with "."
3. Notification sent immediately (no polling delay)

**Critical**: Update `TEMP_EXT` list in [utils/monitor.py#L7](../utils/monitor.py#L7) when supporting new download managers.

### UI Logging
- `MainWindow.add_log()` appends to `QListWidget` with max 100 items (circular buffer)
- All errors/status messages go through this channel, not just `print()`
- Used for user feedback AND debugging

### System Tray Behavior
- App hides to tray on close (not exit) via `closeEvent(event.ignore())`
- Tray icon context menu: "Show" / "Quit"
- Left-click tray icon shows window

## Dependencies & Integrations
- **PyQt6**: GUI framework; requires Python 3.8+
- **watchdog**: File system monitoring; cross-platform observer pattern
- **plyer**: Fallback desktop notifications if Qt tray unavailable

## When Adding Features

### New Monitoring Rules
Edit `MonitorHandler.on_created()` / `on_moved()` → add logic before `self.callback()`

### Config File Additions
1. Update [config.json](../config.json) schema example
2. Add default handling in `MainWindow.load_config()`
3. Test round-trip: load → modify → save → reload

### UI Changes
- Keep threaded operations in `FolderMonitorWorker`, GUI updates via signals
- Always log state changes via `add_log()` for UX transparency
- Test system tray edge cases (minimize, close, tray click)

## Common Pitfalls
- **Threading**: Accessing `self.config` from monitor thread → use signals/slots only
- **File encoding**: JSON/config always UTF-8; Windows paths use forward slashes in config
- **Temp file detection**: Extensions are case-insensitive; add to `TEMP_EXT` before release
