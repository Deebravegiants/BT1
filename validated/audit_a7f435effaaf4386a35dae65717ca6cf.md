### Title
Webhook `shop-domain` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content solely from the raw request body, while the `shop` (tenant) is read from a separate, unauthenticated header. This breaks the binding `hmac_signed_shop == request.shop`, letting anyone who can obtain one validly-signed webhook body (e.g., by installing the app on a shop they control) replay it against the same endpoint with a forged `x-shopify-shop-domain`/`shopify-shop-domain` header pointing at a victim shop, while still passing HMAC verification.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `Request#shop` is read straight from an attacker-controllable HTTP header with no cryptographic binding to that body: [2](#0-1) [3](#0-2) 

`Registry.process` verifies the HMAC over the body only, then trusts `request.shop` as the tenant identity that is handed to the app's webhook handler: [4](#0-3) 

Because the same `api_secret_key` is shared across every shop that has the app installed, an attacker who installs the app on their own store receives a webhook whose body+HMAC pair is valid for that `api_secret_key`. Since the HMAC never covers the `shop-domain` header, the attacker can resend that exact `(body, hmac)` pair to the app's public webhook endpoint while substituting a victim shop's domain in the `shop-domain` header. `Utils::HmacValidator.validate` will still succeed because it only recomputes/compares the signature over `to_signable_string` (the body): [5](#0-4) 

The handler then receives `WebhookMetadata` with the forged `shop` value, so any app logic keyed by `data.shop` (e.g., "look up/update this shop's order record", "delete this shop's cached data") operates on the wrong tenant.

### Impact Explanation
This crosses a tenant boundary: an attacker-controlled, validly-authenticated webhook payload can be attributed to an arbitrary victim `shop` domain because the identity field the app trusts (`request.shop`) is disjoint from the field actually protected by the HMAC (`raw_body`). Depending on how the host app's webhook handler uses `data.shop` (typical usage: looking up the shop's session/store and applying the webhook body to it), this enables cross-tenant data corruption/injection — satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Exploitation requires the attacker to be able to install the app on at least one shop they control (a normal, unprivileged action for any Shopify merchant/developer for a public app) and to be able to send arbitrary HTTP requests to the app's public webhook endpoint (which is by definition internet-reachable). No access token, `client_secret`, or privileged account is needed beyond what any installer of the app already has.

### Recommendation
Include the tenant-identifying headers (`shop-domain`, and ideally `topic`/`webhook-id`) in the signable content that is HMAC-verified, or otherwise cryptographically bind the shop domain to the signed payload before trusting it in `Registry.process`/`WebhookMetadata`. At minimum, document and enforce that host applications must cross-check `data.shop` against a shop they know to have installed the app (e.g. an existing stored session) rather than trusting it outright.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker.myshopify.com` and receives a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's shared `api_secret_key`), `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker replays the same `B`/`H` to the app's public webhook endpoint but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H` (`lib/shopify_api/utils/hmac_validator.rb:26-31`).
4. `Registry.process` builds `WebhookMetadata` with `shop: "victim.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198-199`) and invokes the app's handler as if the legitimately-signed payload came from `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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

**File:** lib/shopify_api/webhooks/request.rb (L66-70)
```ruby

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
