Confirmed: `AuthQuery#to_signable_string` includes `shop` in the signed OAuth callback parameters, so that binding is intact — the HMAC does cover `shop` there. But for webhooks, `Request#to_signable_string` is only `@raw_body` (the JSON body), while `Request#shop` is read from the unsigned `x-shopify-shop-domain`/`shopify-shop-domain` header. That header is passed straight through to the handler via `WebhookMetadata.new(... shop: request.shop ...)` without ever being checked against the HMAC. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Title
Webhook `shop` domain is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking `Utils::HmacValidator.validate(request)`, which computes the HMAC over `request.to_signable_string`. For webhooks, `to_signable_string` returns only the raw request body — it never includes the `shop` value. The `shop` identity is instead read directly from an attacker-controllable HTTP header (`x-shopify-shop-domain`/`shopify-shop-domain`) and forwarded unauthenticated into `WebhookMetadata`, which is the only tenant identifier a handler receives to determine which shop the event belongs to.

### Finding Description
The equality that should hold is: `shop bound in HMAC == shop passed to handler`. Instead:
- `Utils::HmacValidator.validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the header-supplied `hmac` value.
- For `Webhooks::Request`, `to_signable_string` returns `@raw_body` only [2](#0-1) , so the signature verifies the body bytes exclusively.
- `shop` is read from `shopify_header("shop-domain")`, an HTTP header not included in the signed material [5](#0-4) .
- `Registry.process` raises only if the HMAC itself is invalid, then forwards `request.shop` straight to the handler as the tenant identifier: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [6](#0-5) .

Because a single app-wide `api_secret_key` signs webhooks for every shop that installs the app, an attacker who installs the app on a shop they control (or who otherwise obtains one legitimately-signed webhook payload/body+HMAC pair) can replay that exact body+HMAC pair to the app's webhook endpoint while substituting a victim's `x-shopify-shop-domain` value. The HMAC still validates (it never covered `shop`), and `Registry.process` happily hands the handler a `WebhookMetadata` claiming the payload belongs to the victim shop. This directly contrasts with `Auth::Oauth::AuthQuery`, where `shop` **is** included in the signed parameter set [7](#0-6) , showing the webhook path is inconsistent with the library's own OAuth callback design.

### Impact Explanation
This breaks the tenant boundary that host applications rely on: `WebhookMetadata#shop` is the field applications use to look up/act on a specific merchant's session, store record, or data. An attacker can force the library to attribute a webhook event/body to a shop of their choosing without possessing that shop's credentials, enabling cross-tenant data confusion in any handler that trusts `data.shop` (e.g., updating billing state, order data, or app-uninstall handling for a shop the attacker doesn't control) — this matches the Critical "cross-tenant access" category, since the gem itself, not host misuse, fails to bind the identity field into the authenticated payload.

### Likelihood Explanation
Any developer using the app under normal, documented usage (installing the app on their own shop to get valid webhook deliveries) can obtain a valid `(body, hmac)` pair signed with the app's shared secret, then simply resend it with a modified `shop-domain` header — no access to `api_secret_key`, tokens, or the victim's credentials is required. This is a straightforward HTTP replay exploitable by any internet-reachable webhook endpoint.

### Recommendation
Include `shop` (and ideally `topic`, `webhook_id`) in the material that is verified, e.g. bind the signed body to the expected shop by having `Registry.process` (or the host callback) confirm `request.shop` against a known/allow-listed set of installed shops before dispatch, or otherwise cryptographically tie the header value to the signature (for example by requiring callers to pass the expected shop and comparing it, or documenting/enforcing that consumers must independently validate `data.shop` against their session store before trusting it).

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; capture a legitimate webhook delivery: raw body `B` and header `x-shopify-hmac-sha256: H` (valid because `H = HMAC(api_secret_key, B)`).
2. Resend a request to the app's webhook endpoint with the same body `B`, same `x-shopify-hmac-sha256: H`, but header `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H` [4](#0-3) .
4. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)` even though the event never originated from `victim.myshopify.com` [8](#0-7) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L34-43)
```ruby
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
