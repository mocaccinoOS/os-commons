/* === This file is part of Calamares - <http://github.com/calamares> ===
 *
 *   Copyright 2015, Teo Mrnjavac <teo@kde.org>
 *
 *   Calamares is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   Calamares is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with Calamares. If not, see <http://www.gnu.org/licenses/>.
 */

import QtQuick 2.0;
import calamares.slideshow 1.0;

Presentation
{
    id: presentation

    Timer {
        interval: 8000
        running: true
        repeat: true
        onTriggered: presentation.goToNextSlide()
    }

    // Slides are 1240x698 (about 16:9). PreserveAspectCrop fills the slideshow
    // area without stretching; keep content inside a ~5% safe margin.

    // MOS_1 - Welcome: Luet package manager, layers and rolling updates
    Slide {
        anchors.fill: parent
        Rectangle { anchors.fill: parent; color: "#20262A" }
        Image {
            anchors.fill: parent
            source: "images/MOS_1.png"
            fillMode: Image.PreserveAspectCrop
            smooth: true
            mipmap: true
        }
    }

    // MOS_2 - Performance: optional x86-64-v3 layer, sched_ext schedulers, compressed memory
    Slide {
        anchors.fill: parent
        Rectangle { anchors.fill: parent; color: "#20262A" }
        Image {
            anchors.fill: parent
            source: "images/MOS_2.png"
            fillMode: Image.PreserveAspectCrop
            smooth: true
            mipmap: true
        }
    }

    // MOS_3 - Desktops: the five editions (KDE Plasma, XFCE, GNOME, MATE, COSMIC)
    Slide {
        anchors.fill: parent
        Rectangle { anchors.fill: parent; color: "#20262A" }
        Image {
            anchors.fill: parent
            source: "images/MOS_3.png"
            fillMode: Image.PreserveAspectCrop
            smooth: true
            mipmap: true
        }
    }

    // MOS_4 - Gaming: Steam with GameMode, Wine from the Community Repository, launchers
    Slide {
        anchors.fill: parent
        Rectangle { anchors.fill: parent; color: "#20262A" }
        Image {
            anchors.fill: parent
            source: "images/MOS_4.png"
            fillMode: Image.PreserveAspectCrop
            smooth: true
            mipmap: true
        }
    }

    // MOS_5 - Work and create: GIMP, Inkscape, Krita, office suite, email, calendar, video chat
    Slide {
        anchors.fill: parent
        Rectangle { anchors.fill: parent; color: "#20262A" }
        Image {
            anchors.fill: parent
            source: "images/MOS_5.png"
            fillMode: Image.PreserveAspectCrop
            smooth: true
            mipmap: true
        }
    }

    // MOS_6 - Dev and science: VS Code, Git, Python, GNU Radio, SDR, data analysis
    Slide {
        anchors.fill: parent
        Rectangle { anchors.fill: parent; color: "#20262A" }
        Image {
            anchors.fill: parent
            source: "images/MOS_6.png"
            fillMode: Image.PreserveAspectCrop
            smooth: true
            mipmap: true
        }
    }

    // MOS_7 - Open and secure: open source on Codeberg, Vajo rollback, privacy defaults
    Slide {
        anchors.fill: parent
        Rectangle { anchors.fill: parent; color: "#20262A" }
        Image {
            anchors.fill: parent
            source: "images/MOS_7.png"
            fillMode: Image.PreserveAspectCrop
            smooth: true
            mipmap: true
        }
    }

    // MOS_8 - Support us: QR code to the donation page (mocaccino.org/docs/donate)
    Slide {
        anchors.fill: parent
        Rectangle { anchors.fill: parent; color: "#20262A" }
        Image {
            anchors.fill: parent
            source: "images/MOS_8.png"
            fillMode: Image.PreserveAspectCrop
            smooth: true
            mipmap: true
        }
    }
}
