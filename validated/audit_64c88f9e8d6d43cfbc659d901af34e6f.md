Based on my analysis, this is the core finding: the webhook's `shop` field is asserted from an HTTP header but is **not covered by the HMAC signature**, which only signs the raw body.### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` extracts the `shop` field from the unauthenticated `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header, while `Utils::HmacValidator` only verifies the HMAC over the raw request body. The `shop` value is never part of the signed material, so an attacker who can obtain one valid `(body, hmac)` pair signed with the app's `client_secret` can replay that body with an arbitrary `shop-domain` header and the HMAC will still verify, letting the attacker impersonate any other merchant's shop in `Registry.process`.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) 

`to_signable_string` returns only `@raw_body`, so `HmacValidator.validate` computes and compares the signature solely against the body bytes: [2](#0-1) 

`Request#shop` is read straight from a header that is not part of that signable string: [3](#0-2) 

`Registry.process` validates the HMAC of the body, then constructs `WebhookMetadata` using `request.shop` — a value that was never authenticated — and hands it directly to the app's handler: [4](#0-3) [5](#0-4) 

The identity binding that should hold is: `hmac == HMAC(client_secret, shop || body)`. Instead the gem only enforces `hmac == HMAC(client_secret, body)`, i.e., **the shop field is a field acted upon (used as the tenant identity passed to the handler) but not covered by the HMAC** — the exact bug-class pattern from the referenced report (a value trusted for a security decision that is not included in the integrity check that supposedly authenticates it).

Because a single app's `client_secret` (the HMAC key) is shared across every merchant/shop that has installed the app, any shop owner who legitimately installs the app can capture one authentic `(body, x-shopify-hmac-sha256)` pair from Shopify's own webhook delivery to their own store, and then POST that exact body to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. The HMAC still validates (it never depended on the shop header), and `Registry.process` will invoke the app's handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: <attacker-controlled-but-genuinely-signed-content>, ...)`.

### Impact Explanation
This breaks the shop-identity binding that host applications rely on to route webhook payloads to the correct tenant's data. Depending on how the host application uses `WebhookMetadata#shop` (e.g., to look up the corresponding session/store record and apply the payload), this enables cross-tenant data confusion/injection: an attacker-controlled shop can cause data nominally "belonging" to a victim shop to be processed by the app, without ever needing the victim's credentials, access token, or `client_secret`. This satisfies the Critical "cross-tenant access" impact category — the gem's own signature-verification API returns a false-positive trust decision for a forged tenant identity.

### Likelihood Explanation
The attacker only needs to be an ordinary Shopify merchant who has installed the vulnerable app on their own store (an unprivileged-relative-to-other-tenants position) and network access to POST directly to the app's public webhook endpoint — both trivially available to any internet user who installs the app. No leaked secrets, TLS interception, or social engineering are required; the flaw is purely in how the gem constructs and validates the HMAC input in `Request`/`HmacValidator`.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the signable material verified against the HMAC, or otherwise cryptographically bind the `shop` header to the signed payload before trusting it. If Shopify's wire protocol truly only signs the raw body (matching Shopify's documented webhook HMAC scheme), the gem should not expose `request.shop` as a trusted identity to `WebhookHandler` without documenting to consumers that `shop` is unauthenticated and must be independently verified (e.g., cross-checked against a known/allow-listed shop or the shop derived from a previously stored webhook subscription id) before being used for tenant-scoped decisions.

### Proof of Concept
1. App `X` is installed on attacker's shop `attacker.myshopify.com` and on victim's shop `victim.myshopify.com`.
2. Shopify delivers a legitimate webhook to `X`'s endpoint for `attacker.myshopify.com`:
   - Headers: `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of raw_body with client_secret>`, raw body `B`.
3. Attacker replays the exact same raw body `B` and the exact same `x-shopify-hmac-sha256` value to `X`'s endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate` recomputes `HMAC(client_secret, B)` and it matches the replayed signature (per `lib/shopify_api/utils/hmac_validator.rb:26-31` and `lib/shopify_api/webhooks/request.rb:36-38`), because the shop header was never part of the signed content.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) passes `WebhookMetadata.new(shop: "victim.myshopify.com", body: <parsed B>, ...)` to the app's handler, which now believes the (attacker-controlled) content in `B` legitimately originated from `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
