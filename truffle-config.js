module.exports = {
  networks: {
    development: {
      host: "127.0.0.1",    // Localhost
      port: 7545,           // Standard Ganache port
      network_id: "*",      // Match any network id
    }
  },

  // Configure your compilers
  compilers: {
    solc: {
      version: "0.8.21",   // Use the version compatible with your contract
    }
  }
};
