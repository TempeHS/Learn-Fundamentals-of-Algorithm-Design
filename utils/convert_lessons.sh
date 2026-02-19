#!/bin/bash
# Simple wrapper script to convert all markdown lessons to PDF

echo "=================================================="
echo "Converting Algorithm Design Lessons to PDF"
echo "=================================================="
echo ""

# Check for nbconvert (needed for ipynb -> markdown)
if ! python3 -c "import nbconvert" 2>/dev/null; then
    echo "⚠️  nbconvert not installed!"
    echo ""
    echo "Would you like to install dependencies now? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        bash utils/install_dependencies.sh
    else
        echo "❌ Cannot proceed without nbconvert."
        echo "Run: bash utils/install_dependencies.sh"
        exit 1
    fi
fi

# Check if dependencies are installed
if ! python3 -c "import weasyprint" 2>/dev/null; then
    echo "⚠️  Dependencies not installed!"
    echo ""
    echo "Would you like to install them now? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        bash utils/install_dependencies.sh
    else
        echo "❌ Cannot proceed without dependencies."
        echo "Run: bash utils/install_dependencies.sh"
        exit 1
    fi
fi

# Navigate to project root if script is run from utils/
if [ "$(basename "$PWD")" = "utils" ]; then
    cd ..
fi

# Convert notebooks to markdown first
echo "➡️  Converting notebooks (.ipynb) to markdown..."
python3 utils/ipynb_to_md.py --input-dir "lessons" --output-dir "other_formats/markdown_lessons" --verbose

# Run the markdown to PDF conversion
python3 utils/md_to_pdf.py --directory "other_formats/markdown_lessons" --output-dir "other_formats/pdf_lessons" --verbose

echo ""
echo "=================================================="
echo "✓ Conversion Complete!"
echo "=================================================="
echo ""
echo "📁 PDF files saved to: other_formats/pdf_lessons/"
echo ""
