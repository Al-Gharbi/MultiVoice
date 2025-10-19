# MultiVoice
Multi-user voice chat application for local networks - Real-time group audio communication

### Multi-User Voice Chat Application 

A real-time voice chat solution for multiple users.

A real-time voice chat application built with Python that allows users to communicate over a network using UDP protocol. This application features a client-server architecture with audio streaming capabilities.

## Table of Contents
- [First Step: Local Network Setup](#first-step-local-network-setup)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Technical Details](#technical-details)
- [Troubleshooting](#troubleshooting)
- [Audio Quality Optimization](#audio-quality-optimization)

## First Step: Local Network Setup

**Before running the application, you MUST ensure all devices are on the same local network:**

### For Home/Office Network:
1. Connect all computers to the same Wi-Fi network
2. Or connect all devices to the same router via Ethernet cables
3. Verify connectivity by pinging between devices

### For Hotspot Setup:
1. Use one computer as a hotspot:
   - **Windows**: Settings → Mobile Hotspot → Turn on
   - **Mac**: System Preferences → Sharing → Internet Sharing
2. Connect other devices to this hotspot
3. Ensure all devices can see each other on the network

### Verify Network Connection:
```bash
# Find your IP address:
# Windows:
ipconfig

# Mac/Linux:
ifconfig

# Test connection between devices:
ping [other-device-ip]
```

## Features

### Core Functionality
- **Real-time Voice Communication**: Low-latency audio streaming between multiple clients
- **Client-Server Architecture**: Centralized server managing multiple client connections
- **UDP Protocol**: Efficient data transmission for real-time audio
- **Automatic Connection Management**: Heartbeat system to maintain active connections
- **Cross-Platform Compatibility**: Works on Windows, macOS, and Linux

### User Experience
- **Automatic Recording**: Starts recording immediately upon connection
- **Mute/Unmute Control**: Toggle audio transmission with a single keypress
- **Interactive Interface**: Simple keyboard-based controls
- **Connection Status**: Real-time connection monitoring and management
- **Audio Buffer Management**: Smooth playback with optimized buffering

### Technical Features
- **Error Handling**: Robust error handling for network and audio operations
- **Logging System**: Comprehensive event logging on server side
- **Resource Management**: Proper cleanup of sockets and audio streams
- **Configurable Parameters**: Adjustable audio quality and network settings

## Installation

### Step 1: Install Python
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check "Add Python to PATH" during installation
4. Verify installation by opening Command Prompt and typing:
   ```bash
   python --version
   ```

### Step 2: Install Required Packages
Open Command Prompt or Terminal and run:

```bash
# Install audio processing library
pip install sounddevice

# Install numerical processing library
pip install numpy
```

### Step 3: Download Project Files
1. Create a project folder:
   ```bash
   mkdir VoiceChatApp
   cd VoiceChatApp
   ```

2. Save the provided files in this folder:
   - `server.py`
   - `client.py`

## Usage

### Running the Server

1. **Find Server IP Address**:
   ```bash
   # Windows:
   ipconfig
   # Look for "IPv4 Address" - usually 192.168.x.x or 10.0.x.x

   # Mac/Linux:
   ifconfig
   # Look for "inet" under your network interface
   ```

2. **Start the Server**:
   ```bash
   python server.py
   ```

3. **Server Output**:
   ```
   [2024-01-01 10:00:00] Server started on 0.0.0.0:12345
   [2024-01-01 10:00:00] Press Ctrl+C to stop the server
   ```

### Running the Client

1. **Basic Connection to Local Server**:
   ```bash
   python client.py --host localhost --name "YourName"
   ```

2. **Connection to Another Computer**:
   ```bash
   python client.py --host 192.168.1.100 --name "YourName"
   ```
   *Replace 192.168.1.100 with the actual server IP address*

3. **Command Line Parameters**:
   - `--host`: Server IP address (default: localhost)
   - `--port`: Server port (default: 12345)
   - `--client-port`: Client listening port (default: 12346)
   - `--name`: Your display name (default: User)

### Client Controls
Once connected, use these keyboard commands:
- **`r`**: Toggle mute/unmute
- **`q`**: Quit application

### Example Session

**On Server Computer**:
```bash
# Find server IP first, then:
python server.py
```

**On Client Computer 1**:
```bash
python client.py --host 192.168.1.100 --name Alice
```

**On Client Computer 2**:
```bash
python client.py --host 192.168.1.100 --name Bob --client-port 12347
```

## Project Structure

### Server (`server.py`)
- **VoiceChatServer Class**: Main server implementation
- **Connection Management**: Handles client registration and heartbeats
- **Audio Routing**: Broadcasts audio to all connected clients
- **Logging System**: Tracks all server activities

### Client (`client.py`)
- **VoiceChatClient Class**: Main client implementation
- **Audio Processing**: Handles recording and playback
- **Network Communication**: Manages server communication
- **User Interface**: Keyboard controls and status display

## Technical Details

### Network Protocol
- **Protocol**: UDP (User Datagram Protocol)
- **Port Configuration**: Default server port 12345, client ports 12346+
- **Control Messages**: JSON-formatted control messages with 'CTRL:' prefix
- **Heartbeat System**: 10-second intervals to maintain connections

### Audio Specifications
- **Sample Rate**: 44.1 kHz (CD quality)
- **Channels**: Mono (1 channel)
- **Format**: 16-bit integer
- **Buffer Size**: 1024 samples per block

## Troubleshooting

### Common Issues

1. **"Connection timeout - server may be offline"**
   - Verify both devices are on same network
   - Check server IP address is correct
   - Disable firewall temporarily for testing

2. **"Port already in use"**
   ```bash
   # Change port number
   python server.py --port 12349
   ```

3. **"Failed to create socket"**
   - Check if another application is using the port
   - Run as administrator (Windows) or use sudo (Linux/macOS)

4. **Audio not working**
   - Verify microphone permissions
   - Check default audio devices in system settings

### Network Troubleshooting Steps:

1. **Verify IP Addresses**:
   - Server and clients must be on same subnet (e.g., all 192.168.1.x)

2. **Check Firewall**:
   - Windows: Allow Python through Windows Defender Firewall
   - Mac: System Preferences → Security & Privacy → Firewall

3. **Test Basic Connectivity**:
   ```bash
   # From client computer, test if server is reachable:
   ping [server-ip-address]
   ```

## Audio Quality Optimization

### Critical Recommendation: Reduce Speaker Volume to 75% or Less

**Why this is important:**
- **Echo Reduction**: Prevents audio feedback when microphones pick up speaker output
- **Noise Cancellation**: Reduces background noise and acoustic echo
- **Better Clarity**: Improves voice clarity in close-proximity setups
- **Hardware Protection**: Prevents audio distortion and equipment damage

### Steps to Optimize Audio:

1. **System Volume Adjustment**:
   - Windows: Right-click speaker icon → Volume Mixer → Reduce to 75%
   - macOS: Sound Preferences → Output → Reduce volume
   - Linux: Sound Settings → Output → Set to 75%

2. **Physical Setup**:
   - Use headphones instead of speakers when possible
   - Position microphone away from speakers
   - Use directional microphones in group settings

3. **Application Settings**:
   - Keep microphone at reasonable distance (15-30 cm)
   - Use push-to-talk if available
   - Enable noise suppression in system audio settings

### For Best Results:
- **Use headphones** to completely eliminate echo
- **Position microphone** 15-20 cm from your mouth
- **Reduce background noise** by closing windows and turning off fans
- **Test audio levels** before starting important conversations


## Support

For immediate issues:
1. **Check network connectivity first** - this solves 90% of problems
2. Verify all devices are on the same local network
3. Test with one client on the same computer as server first
4. Ensure Python and required packages are properly installed

**Remember**: The most important step is ensuring all devices are connected to the same local network before attempting to use the voice chat application.
