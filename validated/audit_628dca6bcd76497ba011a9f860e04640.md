## Title
Webhook `shop` (and `topic`/`webhook-id`/`api-version`) identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing via replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by checking the HMAC over the raw request body, then hands the *header-derived* `shop`, `topic`, `webhook_id` and `api_version` values straight to the app's handler as trusted tenant/event metadata. None of those header values are part of the signed content, so they can be swapped without invalidating the signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from attacker-visible HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` verifies authenticity using exactly that signable string: [3](#0-2) 

and `HmacValidator.validate` computes/compares the HMAC only over `to_signable_string` (i.e. the raw body), never touching the headers: [4](#0-3) 

The binding the code implicitly assumes is:
`hmac_valid(body) == true` ⇒ `request.shop == the shop that actually sent this event`

but the actual equality enforced is only:
`HMAC_secret(body) == received_hmac`

with `shop` (and `topic`/`webhook_id`) sitting entirely outside that computation. Because every shop that installs the app shares the same app `client_secret`, any merchant who has the app installed (including an attacker who installs the app on their own store) can obtain a genuine `(raw_body, hmac)` pair for their own store's events, then replay that exact body+HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header for a victim shop. `HmacValidator.validate` still succeeds (it only checks the untouched body), and `Registry.process` forwards `shop: request.shop` — the attacker-chosen value — to the app's handler as if it were an authentic event from the victim shop: [5](#0-4) 

### Impact Explanation
This breaks the tenant-identity binding the whole webhook trust model depends on: the app is told "this verified event belongs to shop X" when `shop` was never authenticated. Any application logic that uses `WebhookMetadata#shop` to select which tenant's data/session to mutate (a documented, expected use of the gem's webhook API) can be tricked into applying an attacker-supplied topic/body to a victim shop's data — a cross-tenant access/write primitive achievable by any unprivileged user who can install the app on any store (including their own) and hit the app's public webhook endpoint.

### Likelihood Explanation
Requires only: (1) the ability to install the target app on some shop (trivial for public apps, and even for private/dev apps an attacker with any shop can typically install listed apps), (2) capturing one legitimate webhook delivery for that shop, and (3) replaying the HTTP request to the app's public webhook endpoint with a modified `shop-domain`/`topic` header. No access to `api_secret_key`, tokens, or TLS interception is needed — the HMAC is copied verbatim from a delivery the attacker legitimately received.

### Recommendation
Include the shop domain, topic, and webhook id in the signed content used to compute/verify the HMAC (or, at minimum, require the caller to verify that `request.shop` matches an install/session the app already has on file before trusting it), so that no header value used for tenant or event routing can be altered without invalidating the signature.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. App emits a webhook to the app's registered endpoint: body `{"id":123,...}` with headers `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Topic: orders/create`.
3. Attacker intercepts this legitimate delivery (e.g., via a proxy they control, since it's their own traffic) and replays the identical body and `X-Shopify-Hmac-Sha256` value to the app's public webhook URL, but changes `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over the unchanged raw body and succeeds.
5. The handler receives `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: ..., ...)`, and any app logic keyed on `shop` now operates on `victim-shop.myshopify.com` using attacker-controlled event data.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
