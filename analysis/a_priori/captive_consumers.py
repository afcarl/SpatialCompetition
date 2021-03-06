# SpatialCompetition
# Copyright (C) 2018  Aurélien Nioche, Basile Garcia & Nicolas Rougier
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import string
import tqdm
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.gridspec
# from mpl_toolkits.axes_grid1 import make_axes_locatable


def compute_consumers(x1, x2, V):
    """ Compute the number of unique and shared. """

    U1 = np.where(V[:, x1] == 1)[0]
    U2 = np.where(V[:, x2] == 1)[0]
    S = np.intersect1d(U1, U2)
    U1 = np.setdiff1d(U1, S)
    U2 = np.setdiff1d(U2, S)
    return len(U1), len(U2), len(S)


def captive_consumers(radius, fig_name):

    # Create directories if not already existing
    os.makedirs(os.path.dirname(fig_name), exist_ok=True)

    # Figures' labels
    ind_fig_names = string.ascii_uppercase[:len(radius)]

    # Plot this
    fig = plt.figure(figsize=(10, 5))

    # ax = [[], ] * len(ind_fig_names)
    gs = matplotlib.gridspec.GridSpec(nrows=1, ncols=len(radius) + 1, width_ratios=[1, 1, 0.1])

    for idx, (r, name) in enumerate(zip(radius, ind_fig_names)):

        # Parameters
        seed = 123
        np.random.seed(seed)
        n_position = 100

        # Uniform position
        P = np.linspace(0, 1, n_position, endpoint=True)
        P = (np.round(P * (n_position-1))).astype(int)

        # Same constant radius for each consumer
        R = int(np.round(n_position * r)) * np.ones(n_position, dtype=int)

        # Build the local view for each consumer
        V = np.zeros((n_position, n_position))
        for i in range(n_position):
            lower_bound = max(0, P[i]-R[i])
            upper_bound = min(P[i]+R[i], n_position)
            V[i, lower_bound:upper_bound] = 1

        C1 = np.zeros((n_position, n_position))
        C2 = np.zeros((n_position, n_position))
        S = np.zeros((n_position, n_position))
        G = np.zeros((n_position, n_position))

        for x1 in tqdm.trange(n_position):
            for x2 in range(n_position):
                u1, u2, s = compute_consumers(x1, x2, V)
                C1[x1, x2] = u1
                C2[x1, x2] = u2
                S[x1, x2] = s
                G[x1, x2] = n_position - u1 - u2 - s

        ax = fig.add_subplot(gs[0, idx])

        # Relative to colormap
        cmap = plt.get_cmap("viridis")
        bounds = np.arange(0, 51, 2)
        norm = colors.BoundaryNorm(bounds, cmap.N)

        # Imshow object
        im = ax.imshow(C1, origin='lower', extent=[0, 100, 0, 100], norm=norm)  # , aspect="auto")
        # ax.text(4, 4, name, color="white", fontsize=20, fontweight="bold")

        # Some tuning on axes
        for tick in ax.get_xticklabels():
            tick.set_fontsize("x-large")
        for tick in ax.get_yticklabels():
            tick.set_fontsize("x-large")

        # Add a colorbar for fig at pos (1, 3, 3)
        if idx + 1 == len(ind_fig_names):
            # divider = make_axes_locatable(ax)
            # cax = divider.append_axes("right", size="6%", pad=0.2)
            g = matplotlib.gridspec.GridSpecFromSubplotSpec(nrows=3, ncols=3, subplot_spec=gs[0, idx+1],
                                                            height_ratios=[0.01, 1, 0.01],
                                                            width_ratios=[0.1, 0.9, 0.1])

            cax = fig.add_subplot(g[1, 1])
            plt.colorbar(im, norm=norm, ticks=(0, 25, 50), cax=cax),  # cax=cax)
            cax.tick_params(labelsize=15)
            cax.set_ylabel(ylabel="Number of Firm B captive consumers", fontsize=17)
            # cax.subplots_adjust(left=0.5, right=0.6, top=0.4, bottom=0.1)

        # Customize axes
        ax.set_xticks([0, 50, 100])
        ax.set_xticklabels(["0.0", "0.5", "1.0"])
        ax.set_yticks([0, 50, 100])
        ax.set_yticklabels(["0.0", "0.5", "1.0"])

        # Add a contour
        n_levels = int(C1.max()*16 / (n_position/2))
        ct = ax.contourf(C1, n_levels, origin='lower', vmax=n_position / 2)

        # Indicate middle by horizontal and vertical line
        ax.axhline(50, color="white", linewidth=0.5, linestyle="--", zorder=10)
        ax.axvline(50, color="white", linewidth=0.5, linestyle="--", zorder=10)

        # Name axes
        ax.set_xlabel("Position Firm A", labelpad=10, fontsize=17)

        if idx == 0:
            ax.set_ylabel("Position Firm B", labelpad=10, fontsize=17)
        else:
            ax.set_yticks([])

        # Put a title
        ax.set_title("$r={:.2f}$".format(r), fontsize=18)

        ax.set_aspect(1)

    # Cut margins
    plt.tight_layout()

    # Save fig
    plt.savefig(fig_name)
