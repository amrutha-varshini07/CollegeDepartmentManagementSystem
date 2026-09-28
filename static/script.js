// =====================================================
// SECTION NAVIGATION
// =====================================================

function showSection(sectionId) {

    const sections = document.querySelectorAll(".management-section");

    sections.forEach(function(section) {
        section.classList.add("hidden");
    });

    const selectedSection = document.getElementById(sectionId);

    if (selectedSection) {
        selectedSection.classList.remove("hidden");

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    }
}


// =====================================================
// SEARCH TABLE
// =====================================================

function searchTable(input, tableId) {

    const filter = input.value.toLowerCase().trim();
    const table = document.getElementById(tableId);

    if (!table) {
        return;
    }

    const rows = table.getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) {

        const text = rows[i].innerText.toLowerCase();

        if (text.includes(filter)) {
            rows[i].style.display = "";
        } else {
            rows[i].style.display = "none";
        }
    }
}


// =====================================================
// EMAIL VALIDATION
// =====================================================

function isValidEmail(email) {

    const emailPattern =
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    return emailPattern.test(email);
}


// =====================================================
// PHONE VALIDATION
// =====================================================

function isValidPhone(phone) {

    if (phone === "") {
        return true;
    }

    const phonePattern = /^[0-9]{10}$/;

    return phonePattern.test(phone);
}


// =====================================================
// DEPARTMENT VALIDATION
// =====================================================

function validateDepartment() {

    const name = document.getElementById("department_name").value.trim();
    const code = document.getElementById("department_code").value.trim();
    const email = document.getElementById("department_email").value.trim();
    const phone = document.getElementById("department_phone").value.trim();

    if (name.length < 2) {
        alert("Department name must contain at least 2 characters.");
        return false;
    }

    if (code.length < 2) {
        alert("Department code must contain at least 2 characters.");
        return false;
    }

    if (email !== "" && !isValidEmail(email)) {
        alert("Please enter a valid department email address.");
        return false;
    }

    if (!isValidPhone(phone)) {
        alert("Phone number must contain exactly 10 digits.");
        return false;
    }

    return true;
}


// =====================================================
// FACULTY VALIDATION
// =====================================================

function validateFaculty() {

    const name = document.getElementById("faculty_name").value.trim();
    const email = document.getElementById("faculty_email").value.trim();
    const phone = document.getElementById("faculty_phone").value.trim();
    const department = document.getElementById("faculty_department").value;

    if (name.length < 2) {
        alert("Please enter a valid faculty name.");
        return false;
    }

    if (!isValidEmail(email)) {
        alert("Please enter a valid email address.");
        return false;
    }

    if (!isValidPhone(phone)) {
        alert("Phone number must contain exactly 10 digits.");
        return false;
    }

    if (department === "") {
        alert("Please select a department.");
        return false;
    }

    return true;
}


// =====================================================
// STUDENT VALIDATION
// =====================================================

function validateStudent() {

    const name = document.getElementById("student_name").value.trim();
    const roll = document.getElementById("roll_number").value.trim();
    const email = document.getElementById("student_email").value.trim();
    const phone = document.getElementById("student_phone").value.trim();
    const year = document.getElementById("student_year").value.trim();
    const department = document.getElementById("student_department").value;

    if (name.length < 2) {
        alert("Please enter a valid student name.");
        return false;
    }

    if (roll.length < 2) {
        alert("Please enter a valid roll number.");
        return false;
    }

    if (email !== "" && !isValidEmail(email)) {
        alert("Please enter a valid student email address.");
        return false;
    }

    if (!isValidPhone(phone)) {
        alert("Phone number must contain exactly 10 digits.");
        return false;
    }

    if (year === "") {
        alert("Please enter the student year.");
        return false;
    }

    if (department === "") {
        alert("Please select a department.");
        return false;
    }

    return true;
}


// =====================================================
// COURSE VALIDATION
// =====================================================

function validateCourse() {

    const name = document.getElementById("course_name").value.trim();
    const code = document.getElementById("course_code").value.trim();
    const credits = document.getElementById("credits").value;
    const department = document.getElementById("course_department").value;

    if (name.length < 2) {
        alert("Please enter a valid course name.");
        return false;
    }

    if (code.length < 2) {
        alert("Please enter a valid course code.");
        return false;
    }

    if (credits === "" || credits < 1 || credits > 10) {
        alert("Credits must be between 1 and 10.");
        return false;
    }

    if (department === "") {
        alert("Please select a department.");
        return false;
    }

    return true;
}


// =====================================================
// EDIT DEPARTMENT
// =====================================================

function editDepartment(id, name, code, hod, email, phone) {

    const section = document.getElementById("departments");

    if (section) {
        showSection("departments");
    }

    document.getElementById("department_id").value = id;
    document.getElementById("department_name").value = name;
    document.getElementById("department_code").value = code;
    document.getElementById("hod_name").value = hod;
    document.getElementById("department_email").value = email;
    document.getElementById("department_phone").value = phone;

    const button = document.getElementById("departmentSaveButton");

    if (button) {
        button.textContent = "Update Department";
    }

    const cancelButton =
        document.getElementById("departmentCancelButton");

    if (cancelButton) {
        cancelButton.style.display = "block";
    }
}


// =====================================================
// CANCEL DEPARTMENT EDIT
// =====================================================

function cancelDepartmentEdit() {

    document.getElementById("department_id").value = "";
    document.getElementById("department_name").value = "";
    document.getElementById("department_code").value = "";
    document.getElementById("hod_name").value = "";
    document.getElementById("department_email").value = "";
    document.getElementById("department_phone").value = "";

    document.getElementById("departmentSaveButton").textContent =
        "Add Department";

    document.getElementById("departmentCancelButton").style.display =
        "none";
}


// =====================================================
// EDIT FACULTY
// =====================================================

function editFaculty(id, name, email, phone, designation, department) {

    const section = document.getElementById("faculty");

    if (section) {
        showSection("faculty");
    }

    document.getElementById("faculty_id").value = id;
    document.getElementById("faculty_name").value = name;
    document.getElementById("faculty_email").value = email;
    document.getElementById("faculty_phone").value = phone;
    document.getElementById("designation").value = designation;
    document.getElementById("faculty_department").value = department;

    const button = document.getElementById("facultySaveButton");

    if (button) {
        button.textContent = "Update Faculty";
    }

    const cancelButton =
        document.getElementById("facultyCancelButton");

    if (cancelButton) {
        cancelButton.style.display = "block";
    }
}


// =====================================================
// CANCEL FACULTY EDIT
// =====================================================

function cancelFacultyEdit() {

    document.getElementById("faculty_id").value = "";
    document.getElementById("faculty_name").value = "";
    document.getElementById("faculty_email").value = "";
    document.getElementById("faculty_phone").value = "";
    document.getElementById("designation").value = "";
    document.getElementById("faculty_department").value = "";

    document.getElementById("facultySaveButton").textContent =
        "Add Faculty";

    document.getElementById("facultyCancelButton").style.display =
        "none";
}


// =====================================================
// EDIT STUDENT
// =====================================================

function editStudent(id, name, roll, email, phone, year, department) {

    const section = document.getElementById("students");

    if (section) {
        showSection("students");
    }

    document.getElementById("student_id").value = id;
    document.getElementById("student_name").value = name;
    document.getElementById("roll_number").value = roll;
    document.getElementById("student_email").value = email;
    document.getElementById("student_phone").value = phone;
    document.getElementById("student_year").value = year;
    document.getElementById("student_department").value = department;

    const button = document.getElementById("studentSaveButton");

    if (button) {
        button.textContent = "Update Student";
    }

    const cancelButton =
        document.getElementById("studentCancelButton");

    if (cancelButton) {
        cancelButton.style.display = "block";
    }
}


// =====================================================
// CANCEL STUDENT EDIT
// =====================================================

function cancelStudentEdit() {

    document.getElementById("student_id").value = "";
    document.getElementById("student_name").value = "";
    document.getElementById("roll_number").value = "";
    document.getElementById("student_email").value = "";
    document.getElementById("student_phone").value = "";
    document.getElementById("student_year").value = "";
    document.getElementById("student_department").value = "";

    document.getElementById("studentSaveButton").textContent =
        "Add Student";

    document.getElementById("studentCancelButton").style.display =
        "none";
}


// =====================================================
// EDIT COURSE
// =====================================================

function editCourse(id, name, code, credits, department) {

    const section = document.getElementById("courses");

    if (section) {
        showSection("courses");
    }

    document.getElementById("course_id").value = id;
    document.getElementById("course_name").value = name;
    document.getElementById("course_code").value = code;
    document.getElementById("credits").value = credits;
    document.getElementById("course_department").value = department;

    const button = document.getElementById("courseSaveButton");

    if (button) {
        button.textContent = "Update Course";
    }

    const cancelButton =
        document.getElementById("courseCancelButton");

    if (cancelButton) {
        cancelButton.style.display = "block";
    }
}


// =====================================================
// CANCEL COURSE EDIT
// =====================================================

function cancelCourseEdit() {

    document.getElementById("course_id").value = "";
    document.getElementById("course_name").value = "";
    document.getElementById("course_code").value = "";
    document.getElementById("credits").value = "";
    document.getElementById("course_department").value = "";

    document.getElementById("courseSaveButton").textContent =
        "Add Course";

    document.getElementById("courseCancelButton").style.display =
        "none";
}


// =====================================================
// CONNECT VALIDATION TO FORMS
// =====================================================

document.addEventListener("DOMContentLoaded", function() {

    const departmentForm =
        document.querySelector('form[action*="save_department"]');

    const facultyForm =
        document.querySelector('form[action*="save_faculty"]');

    const studentForm =
        document.querySelector('form[action*="save_student"]');

    const courseForm =
        document.querySelector('form[action*="save_course"]');


    if (departmentForm) {
        departmentForm.addEventListener("submit", function(event) {

            if (!validateDepartment()) {
                event.preventDefault();
            }

        });
    }


    if (facultyForm) {
        facultyForm.addEventListener("submit", function(event) {

            if (!validateFaculty()) {
                event.preventDefault();
            }

        });
    }


    if (studentForm) {
        studentForm.addEventListener("submit", function(event) {

            if (!validateStudent()) {
                event.preventDefault();
            }

        });
    }


    if (courseForm) {
        courseForm.addEventListener("submit", function(event) {

            if (!validateCourse()) {
                event.preventDefault();
            }

        });
    }

});
