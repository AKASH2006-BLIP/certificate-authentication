// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract CertificateValidator {
    mapping(bytes32 => bool) public certificateHashes;
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner can call this function.");
        _;
    }

    function addCertificate(bytes32 certificateHash) public onlyOwner {
        require(!certificateHashes[certificateHash], "Certificate hash already exists.");
        certificateHashes[certificateHash] = true;
    }

    function isAuthentic(bytes32 certificateHash) public view returns (bool) {
        return certificateHashes[certificateHash];
    }
}