const hre = require("hardhat");

async function main() {
  const address = "0xF3338Aa1517445fDdd45596431c7Ec0afB6223b5";
  const Counter = await hre.ethers.getContractAt("Counter", address);

  // Read current count
  console.log("Current count:", await Counter.getCount());

  // Increment
  const tx = await Counter.increment();
  await tx.wait();

  // Read updated count
  console.log("Updated count:", await Counter.getCount());
}

main().catch(console.error);

