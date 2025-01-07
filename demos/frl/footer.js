	// Get the current year from the system
    const currentYear = new Date().getFullYear();

    // Create the footer HTML dynamically with the current year
const add_HTML = `
<footer class="bg-blue text-white mt-5 py-3">
    <div class="container text-center">
        <p>&copy; ${currentYear} Frontier Research Library. All rights reserved.</p>
    </div>
</footer>
`;

// Insert the footer into the document
document.writeln(add_HTML);