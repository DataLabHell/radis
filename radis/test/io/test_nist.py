# -*- coding: utf-8 -*-
"""
Test the NIST ASD parser



"""

from io import StringIO

import pytest

from radis.api.nistapi import nist2df

# Real NIST ASD response for Na I between 588 and 590 nm, in the tab-delimited
# format requested by NISTDatabaseManager.fetch_urlnames (format=3, line_out=1,
# enrg_out=on, g_out=on). Kept inline so the test needs no network.
ASD_NA_I = (
    "ritz_wl_air(nm)\tAki(s^-1)\tAcc\tEi(cm-1)\tEk(cm-1)\tg_i\tg_k\tType\t\n"
    '"588.995094"\t"6.16e+07"\tAA\t"0.00000"\t"16973.36619"\t2\t4\t\t\n'
    '"589.592424"\t"6.14e+07"\tAA\t"0.00000"\t"16956.17025"\t2\t2\t\t\n'
)


def test_nist2df_keeps_accuracy_grade(*args, **kwargs):
    """The ASD ``Acc`` grade is the only per-line uncertainty estimate NIST
    serves for the transition probability, and is returned next to ``A``."""

    df = nist2df(StringIO(ASD_NA_I), "Na_I")

    assert "Acc" in df.columns
    assert set(df["Acc"]) == {"AA"}
    # the grade qualifies the transition probability it sits next to
    assert list(df.columns).index("Acc") == list(df.columns).index("A") + 1


def test_nist2df_columns_and_values(*args, **kwargs):
    """Level energies, degeneracies and the wavenumber derived from them."""

    df = nist2df(StringIO(ASD_NA_I), "Na_I")

    assert list(df.columns) == [
        "wav",
        "A",
        "Acc",
        "gl",
        "El",
        "gu",
        "Eu",
        "jl",
        "ju",
    ]
    assert len(df) == 2
    # wav is the energy difference, not the tabulated wavelength
    assert set(round(w, 5) for w in df["wav"]) == {16973.36619, 16956.17025}
    assert set(df["El"]) == {0.0}
    assert set(df["gl"]) == {2}
    assert set(df["gu"]) == {4, 2}


if __name__ == "__main__":
    pytest.main(["-v", __file__])
