// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Counter {
    uint256 public count;

    // Increase count by 1
    function increment() public {
        count += 1;
    }

    // Decrease count by 1
    function decrement() public {
        count -= 1;
    }

    // Get current count
    function getCount() public view returns (uint256) {
        return count;
    }
}
