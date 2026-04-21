<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Privacy Policy | Medical Innovation Podcast</title>
  <style>
    @font-face {
      font-family: 'Inter';
      font-style: normal;
      font-weight: 400;
      font-display: swap;
      src: url(https://fonts.gstatic.com/s/inter/v13/UcC73FwrK3iLTeHuS_fvQtMwCp50KnMa1ZL7.woff2) format('woff2');
    }
    :root {
      --primary: #4177FF;
      --primary-dark: #2563eb;
      --accent: #F3F6FF;
      --background: #ffffff;
      --surface: #f8fafc;
      --text: #1e293b;
      --text-secondary: #64748b;
      --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      --card-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05);
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body { font-family: var(--font-primary); background: var(--background); color: var(--text); line-height: 1.6; }

    /* Header */
    header {
      padding: 1.5rem 0;
      background: rgba(255,255,255,0.95);
      box-shadow: 0 4px 20px rgba(0,0,0,0.05);
      position: sticky;
      top: 0;
      z-index: 1000;
    }
    nav { display: flex; justify-content: space-between; align-items: center; max-width: 1400px; margin: 0 auto; padding: 0 2rem; }
    .nav-logo img { height: 72px; object-fit: contain; }
    .nav-links { display: flex; align-items: center; gap: 3rem; }
    .nav-links a {
      color: var(--text-secondary);
      text-decoration: none;
      font-weight: 500;
      font-size: 0.95rem;
      transition: color 0.2s;
    }
    .nav-links a:hover { color: var(--primary); }

    /* Page hero */
    .page-hero {
      padding: 5rem 0 4rem;
      background: var(--surface);
      position: relative;
      overflow: hidden;
    }
    .page-hero::before {
      content: '';
      position: absolute; top: 0; left: 0; right: 0; bottom: 0;
      background: radial-gradient(circle at 10% 20%, rgba(65,119,255,0.05) 0%, transparent 50%),
                  radial-gradient(circle at 90% 80%, rgba(65,119,255,0.03) 0%, transparent 50%);
      pointer-events: none;
    }
    .page-hero .container { position: relative; }
    .page-hero h1 {
      font-size: 3rem;
      font-weight: 800;
      letter-spacing: -0.03em;
      background: linear-gradient(to right, var(--text) 0%, var(--primary) 100%);
      -webkit-background-clip: text;
      background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 0.75rem;
    }
    .page-hero p { color: var(--text-secondary); font-size: 1rem; }

    /* Content */
    .container { max-width: 1400px; margin: 0 auto; padding: 0 2rem; }
    .content-wrap { max-width: 820px; margin: 0 auto; padding: 4rem 2rem 6rem; }

    h2 {
      font-size: 0.75rem;
      font-weight: 700;
      color: var(--primary);
      text-transform: uppercase;
      letter-spacing: 1px;
      margin: 3rem 0 0.75rem;
    }
    h2:first-child { margin-top: 0; }
    p { color: var(--text-secondary); line-height: 1.75; margin-bottom: 1rem; font-size: 0.97rem; }
    ul { margin: 0.5rem 0 1rem 1.25rem; }
    li { color: var(--text-secondary); line-height: 1.75; font-size: 0.97rem; margin-bottom: 0.25rem; }
    a.inline { color: var(--primary); text-decoration: none; }
    a.inline:hover { color: var(--primary-dark); text-decoration: underline; }

    .card {
      background: white;
      border-radius: 24px;
      padding: 2.5rem;
      box-shadow: var(--card-shadow);
      border: 1px solid rgba(0,0,0,0.04);
    }

    /* Footer */
    footer { background: var(--surface); padding: 3rem 0 2rem; border-top: 1px solid rgba(0,0,0,0.06); }
    .footer-bottom {
      max-width: 1400px; margin: 0 auto; padding: 0 2rem;
      display: flex; justify-content: space-between; align-items: center;
    }
    .footer-bottom p { color: var(--text-secondary); font-size: 0.875rem; }
    .footer-bottom-links { display: flex; gap: 2rem; }
    .footer-bottom-links a { color: var(--text-secondary); text-decoration: none; font-size: 0.875rem; transition: color 0.2s; }
    .footer-bottom-links a:hover { color: var(--primary); }

    @media (max-width: 768px) {
      .page-hero h1 { font-size: 2rem; }
      .nav-links { display: none; }
      .footer-bottom { flex-direction: column; gap: 1rem; text-align: center; }
      .footer-bottom-links { flex-direction: column; gap: 0.75rem; align-items: center; }
    }
  </style>
</head>
<body>

<header>
  <nav>
    <a href="https://medicalinnovationpod.com" class="nav-logo">
      <img src="/images/logo-transparent.png" alt="Medical Innovation Podcast">
    </a>
    <div class="nav-links">
      <a href="https://medicalinnovationpod.com/#why-listen">Why Listen</a>
      <a href="https://medicalinnovationpod.com/#hosts">Hosts</a>
      <a href="https://medicalinnovationpod.com/#episodes">Episodes</a>
      <a href="https://medicalinnovationpod.com/#contact">Contact</a>
    </div>
  </nav>
</header>

<div class="page-hero">
  <div class="container">
    <h1>Privacy Policy</h1>
    <p>Last updated: April 21, 2026</p>
  </div>
</div>

<div class="content-wrap">
  <div class="card">

    <h2>Overview</h2>
    <p>
      Medical Innovation Podcast ("we," "us," or "our") operates the TMIP Poster application,
      which automatically publishes podcast clip content to social media platforms including
      TikTok, Instagram, and YouTube. This Privacy Policy explains how we handle data in
      connection with this application.
    </p>

    <h2>Who This Applies To</h2>
    <p>
      This application is a private, internal tool used solely by the operators of the
      Medical Innovation Podcast to publish content to our own social media accounts.
      It is not a consumer-facing product and does not collect data from third parties
      or general users.
    </p>

    <h2>Information We Access</h2>
    <p>When connecting to social media platforms, this application accesses:</p>
    <ul>
      <li><strong>TikTok:</strong> Account access token and open ID, used solely to upload video content to our TikTok account.</li>
      <li><strong>Instagram:</strong> Account access token and user ID, used solely to publish Reels to our Instagram account.</li>
      <li><strong>YouTube:</strong> OAuth refresh token, used solely to upload Shorts to our YouTube channel.</li>
    </ul>
    <p>
      We do not access follower data, direct messages, analytics, or any other account
      information beyond what is strictly required to publish content.
    </p>

    <h2>How We Store Data</h2>
    <p>
      All authentication tokens are stored as encrypted secrets in GitHub Actions,
      accessible only to the repository owner. Tokens are never logged, transmitted
      to third parties, or stored in plain text.
    </p>

    <h2>How We Use Data</h2>
    <p>
      Authentication tokens are used exclusively to post pre-approved podcast clip videos
      to our own social media accounts on a scheduled basis. No data is sold, shared,
      or used for advertising.
    </p>

    <h2>Data Retention</h2>
    <p>
      Access tokens are refreshed automatically as required by each platform and are
      revocable at any time through the respective platform's app settings. We do not
      retain any platform data beyond what is needed for the current posting cycle.
    </p>

    <h2>Third-Party Platforms</h2>
    <p>Our use of TikTok, Instagram, and YouTube APIs is subject to the terms and privacy policies of those platforms:</p>
    <ul>
      <li><a class="inline" href="https://www.tiktok.com/legal/privacy-policy" target="_blank">TikTok Privacy Policy</a></li>
      <li><a class="inline" href="https://privacycenter.instagram.com/policy" target="_blank">Instagram / Meta Privacy Policy</a></li>
      <li><a class="inline" href="https://policies.google.com/privacy" target="_blank">Google / YouTube Privacy Policy</a></li>
    </ul>

    <h2>Contact</h2>
    <p>
      Questions about this policy can be directed to:<br>
      <a class="inline" href="mailto:contact@medicalinnovationpod.com">contact@medicalinnovationpod.com</a>
    </p>

  </div>
</div>

<footer>
  <div class="footer-bottom">
    <p>&copy; <?php echo date('Y'); ?> Medical Innovation Podcast</p>
    <div class="footer-bottom-links">
      <a href="https://medicalinnovationpod.com">Home</a>
      <a href="/privacy-policy.php">Privacy Policy</a>
      <a href="/terms-of-service.php">Terms of Service</a>
    </div>
  </div>
</footer>

</body>
</html>
