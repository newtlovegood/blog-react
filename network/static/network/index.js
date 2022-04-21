
document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('#create-post-btn').addEventListener('click', createPost);
    let editButtons = document.querySelectorAll('.edit-post-btn')
     Array.prototype.forEach.call(editButtons, (el) =>
      el.addEventListener('click', openEditing)
  )
    let likeButtons = document.querySelectorAll('.like-btn')
    Array.prototype.forEach.call(likeButtons, (el) =>
        el.addEventListener('click', likePost)
    )

    let commentButtons = document.querySelectorAll('.comments-btn')
    Array.prototype.forEach.call(commentButtons, (el) =>
        el.addEventListener('click', getComments)
    )
});


function createPost(e) {
    e.preventDefault();
    fetch('/posts', {
      method: 'POST',
      body: JSON.stringify({content: document.querySelector('#post-content').value}),
        credentials : 'same-origin', // For same origin requests
        headers: {"X-CSRFToken": csrftoken},
    })
    .then(response => response.json())
    .then(result => {
        // Print result
        console.log(result.post_id);
        getNewPostInserted(result.post_id);
        document.querySelector('#post-content').value = '';
    });
}

function getNewPostInserted(id) {
    fetch('/posts/' + id)
        .then(response => response.json())
        .then(post => {
            const div = document.createElement('div');
            div.innerHTML += `<p><a href="">${post.user}</a></p>
                    <p id="post-content">${post.content}</p>
                    <p>${post.timestamp}</p>
                    <div>
                    </div>
                    <hr>`;

            document.querySelector('#posts-container').prepend(div) ;
        })

}

function editPost(e) {
    const postId = e.target.getAttribute('data-post-id');
    const initContentContainer = document.querySelector(`p[data-content-id="${postId}"]`);
    const initPostDate = e.target.parentElement.parentElement.querySelector('.post-date')
    fetch('posts/' + postId, {
      method: 'PUT',
      body: JSON.stringify({content: initContentContainer.firstChild.value}),
        credentials : 'same-origin', // For same origin requests
        headers: {"X-CSRFToken": csrftoken},
    })
        .then(response => response.json())
        .then(data => {
            // set the button to EDIT
            e.target.innerHTML = 'Edit';
            e.target.classList.replace('btn-success', 'btn-primary');
            // remove listener
            e.target.removeEventListener('click', editPost);
            // add event listener
            e.target.addEventListener('click', openEditing);
            // change the input to text
            initContentContainer.innerHTML = initContentContainer.firstChild.value;
            // update timestamp
            initPostDate.innerHTML = data.timestamp;
        });

}

function openEditing(e) {
    const postId = e.target.getAttribute('data-post-id');
    const initContentContainer = document.querySelector(`p[data-content-id="${postId}"]`)
    initContentContainer.innerHTML = `<textarea>${initContentContainer.innerHTML}</textarea>`;
    e.target.removeEventListener('click', openEditing);
    e.target.classList.replace('btn-primary', 'btn-success');
    e.target.innerHTML = 'Save';
    e.target.addEventListener('click', editPost);

}

function likePost(e) {
    console.log(e.target);
    let idToFollow = e.target.getAttribute('data-post-id');
    fetch('likes/' + idToFollow)
        .then(response => response.json())
        .then(async data => {
            // await new Promise(r => setTimeout(r, 500));
            e.target.parentElement.lastElementChild.innerHTML = data.likes;
            if (data.created === true) {
                // change icon
                e.target.setAttribute("name", "heart")
            } else {
                e.target.setAttribute("name", "heart-outline")
            }
        })
}

// for csrf token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

let csrftoken = getCookie('csrftoken');