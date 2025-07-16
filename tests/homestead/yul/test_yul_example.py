"""Test Yul Source Code Examples."""

import pytest

from ethereum_test_forks import Fork, Frontier, Homestead
from ethereum_test_tools import (
    Account,
    Alloc,
    Environment,
    StateTestFiller,
    Transaction,
    YulCompiler,
)

from config import EnvConfig

@pytest.mark.valid_from("Homestead")
def test_yul(state_test: StateTestFiller, pre: Alloc, yul: YulCompiler, fork: Fork):
    """Test YUL compiled bytecode."""
    env = Environment()

    contract_address = pre.deploy_contract(
        code=yul(
            """
            {
                function f(a, b) -> c {
                    c := add(a, b)
                }

                sstore(0, f(1, 2))
                return(0, 32)
            }
            """
        ),
        balance=0x0BA1A9CE0BA1A9CE,
    )
    sender = pre.fund_eoa(amount=0x0BA1A9CE0BA1A9CE)

    chain_id: int = EnvConfig().remote_nodes[0].chain_id

    tx = Transaction(
        ty=0x0,
        chain_id=chain_id,
        sender=sender,
        to=contract_address,
        gas_limit=500000,
        gas_price=20_000_000_000,
        protected=False if fork in [Frontier, Homestead] else True,
    )

    post = {
        contract_address: Account(
            storage={
                0x00: 0x03,
            },
        ),
    }

    state_test(env=env, pre=pre, post=post, tx=tx)
