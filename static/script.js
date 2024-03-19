// Data Entry Page
const entryForm = document.getElementById("entry-form");

entryForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const formData = {
    childName: document.getElementById("child-name").value,
    parentId: document.getElementById("parent-id").value,
    parentEmail: document.getElementById("parent-email").value,
    gender: document.getElementById("gender").value,
    dob: document.getElementById("dob").value,
  };

  //data submission
  fetch("/submit-data", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(formData),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Data submitted successfully:", data);
      // Reset the form or display a success message
    })
    .catch((error) => {
      console.error("Error submitting data:", error);
    });
});

// Data Display Page
fetch("/get-data")
  .then((response) => response.json())
  .then((data) => {
    const dataTable = document
      .getElementById("data-table")
      .getElementsByTagName("tbody")[0];

    data.forEach((child) => {
      const row = document.createElement("tr");

      const nameCell = document.createElement("td");
      nameCell.textContent = child.childName;
      row.appendChild(nameCell);

      const parentIdCell = document.createElement("td");
      parentIdCell.textContent = child.parentId;
      row.appendChild(parentIdCell);

      const parentEmailCell = document.createElement("td");
      parentEmailCell.textContent = child.parentEmail;
      row.appendChild(parentEmailCell);

      const genderCell = document.createElement("td");
      genderCell.textContent = child.gender;
      row.appendChild(genderCell);

      const dobCell = document.createElement("td");
      dobCell.textContent = child.dob;
      row.appendChild(dobCell);

      const scheduleCell = document.createElement("td");
      scheduleCell.textContent = child.vaccinationSchedule.join(", ");
      row.appendChild(scheduleCell);

      dataTable.appendChild(row);
    });
  })
  .catch((error) => {
    console.error("Error fetching data:", error);
  });
