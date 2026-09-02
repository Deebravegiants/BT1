### Title
Webhook shop-domain (and topic) header is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the HMAC over the raw request body only, while the `shop-domain`, `topic`, `webhook-id`, and `api-version` values are read from unauthenticated HTTP headers that are never part of the signed material. `Registry.process` accepts any request whose body HMAC validates, then dispatches to the app's handler using the unverified `shop` header as the tenant identity.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are all derived purely from HTTP headers, which are not part of the signable string and thus are never bound to the HMAC: [2](#0-1) 

`Registry.process` validates only the HMAC-over-body via `Utils::HmacValidator.validate(request)`, and then passes the unauthenticated `request.shop` (and `request.topic`) straight to the handler as the tenant identity, with no cross-check that the signed body actually originated for that shop: [3](#0-2) 

`Utils::HmacValidator.validate_signature` calls `verifiable_query.to_signable_string`, i.e., only the body, and compares it to the `hmac` accessor, which again is read straight from an unauthenticated header: [4](#0-3) 

**Broken identity binding (equality that should hold but doesn't):**
`shop_that_produced_the_signed_body == shop_header_used_by_handler`

Because `shop-domain` is outside the HMAC's coverage, an attacker who can obtain any single valid `(raw_body, hmac)` pair signed with the app's shared `client_secret` — trivially available to them by installing the target app on their own shop and capturing one of their own legitimate webhook deliveries — can replay that exact body and HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header for a different, victim shop that also has the app installed. `HmacValidator.validate` will report the request as valid (it only checks the body), and `Registry.process` will invoke the handler with `WebhookMetadata` claiming the payload came from the victim shop.

This is a direct structural analog of the external report's root cause: a value that is *acted upon* (here, the tenant/shop identity used to route and process data) is updated/used without being covered by the integrity check that is supposed to bind it (here, the per-body HMAC), permitting a value from one period/context (one shop) to be misapplied to another (a different shop) — exactly the "field acted on but not covered by the HMAC" pattern called out in this engagement's scope.

### Impact Explanation
This directly matches the accepted "Critical - cross-tenant access" category: a malicious merchant (an unprivileged internet user who merely installs the target app on their own shop — no special privilege, access token, or leaked secret required) can inject arbitrary attacker-chosen webhook payloads that the app will process as belonging to a different tenant shop. Depending on what the app does with webhook data (e.g., updating internal shop records, triggering fulfillment, resetting data on `shop/redact`, etc.), this can corrupt or leak another merchant's data/state, or trigger privileged actions attributed to the wrong tenant.

### Likelihood Explanation
Any user can sign up for a Shopify development/partner account and install a target public app on a shop they control at no cost, and Shopify will deliver real webhooks to that app with valid HMACs signed by the shared `client_secret`. Capturing one `(body, hmac)` pair from their own shop and replaying it against the app's webhook endpoint with a forged `shop-domain` header requires no credentials belonging to the victim shop and no interaction with the victim. The only prerequisite is that the app share a single `client_secret` across all installs (the standard multi-tenant public-app model), which this library's `Context.setup(api_secret_key: ...)` design assumes.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the material that is authenticated, or otherwise re-verify that the header-derived `shop` matches an app-known, expected identity before trusting it:
- At minimum, document/require that consuming apps cross-check `WebhookMetadata#shop` against the shop associated with the webhook subscription/session they expect, rather than trusting the header outright.
- Where feasible, have `Registry.process` require the caller to supply the expected shop (e.g., from the URL path or session context) and assert it matches `request.shop` before dispatch, rather than relying solely on body-HMAC validity.
- Consider also validating `webhook-id` uniqueness/replay windows so a captured `(body, hmac)` cannot be indefinitely replayed under a different shop header.

### Proof of Concept
```ruby
# 1. Attacker installs the target public app on their own store "attacker.myshopify.com"
#    and captures one legitimate webhook delivery, e.g. "orders/create":
raw_body = '{"id":1,"note":"hello"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)
valid_hmac_b64 = Base64.encode64(hmac)   # captured from the real request the attacker's shop received

# 2. Attacker replays the exact same body+hmac to the app's webhook endpoint,
#    but swaps the shop-domain header to a victim shop that also installed the app:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac_b64,     # unchanged, still valid because HMAC only covers raw_body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",  # forged, NOT covered by the HMAC
  "x-shopify-webhook-id" => "attacker-controlled-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# 3. Validation passes because HmacValidator only checks the (unmodified) raw_body:
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

# 4. Registry.process happily dispatches the attacker-chosen payload
#    to the handler, claiming it is for "victim-shop.myshopify.com":
ShopifyAPI::Webhooks::Registry.process(request)
# handler.handle(data: WebhookMetadata.new(topic: "orders/create",
#   shop: "victim-shop.myshopify.com", body: {"id"=>1,"note"=>"hello"}, ...))
```

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
