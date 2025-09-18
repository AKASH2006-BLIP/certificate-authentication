const CertificateValidator = artifacts.require("CertificateValidator");

module.exports = function (deployer) {
  deployer.deploy(CertificateValidator);
};