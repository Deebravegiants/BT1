### Title
Webhook Shop Identity Spoofing via `shop-domain` Header Not Covered by HMAC - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw webhook body, while the `shop` (i.e. `x-shopify-shop-domain` / `shopify-shop-domain`) header is read separately and passed unverified into the handler. `Utils::HmacValidator` only checks the HMAC over the body, so the tenant-identifying `shop` field is not bound to the signature that authenticates the request, letting an attacker with one genuine signed payload replay it while claiming it belongs to a different shop.

### Finding Description
`ShopifyAPI::Webhooks::Request` exposes `shop` from the `shopify-shop-domain`/`x-shopify-shop-domain` header: [1](#0-0) 

but `to_signable_string`, the value that is actually HMAC-verified, only covers `@raw_body`: [2](#0-1) 

`Utils::HmacValidator.validate` computes and compares the signature purely from `to_signable_string`: [3](#0-2) 

`Registry.process` validates the HMAC, then constructs `WebhookMetadata` directly from `request.shop` — a value that was never part of the signed material — and hands it to the app's handler as trusted tenant context: [4](#0-3) 

The binding that should hold is:
`shop authenticated (bound into the HMAC) == shop acted on (WebhookMetadata#shop trusted by the handler)`

Instead, the gem authenticates only the body, and separately trusts the `shop` header verbatim. An attacker can install the target app on their own (attacker-controlled) shop, trigger any webhook topic with attacker-chosen body content, and receive a genuinely Shopify-signed `(body, hmac)` pair. Because the signature never covers the `shop` header, the attacker can replay that exact `(body, hmac)` pair directly to the app's public webhook endpoint while substituting an arbitrary victim `shop-domain` header. `HmacValidator.validate` still succeeds (the body/HMAC pair is valid), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop.

### Impact Explanation
Any app relying on this gem's webhook `shop`/`WebhookMetadata#shop` to key persistence, cache invalidation, or business logic per-tenant can be made to apply attacker-supplied webhook data (order, product, customer, GDPR, etc.) under a victim shop's identity. This is a cross-tenant integrity/confidentiality break — the gem's own signature verification does not protect the field applications use to scope data to a merchant. Under the stated impact taxonomy this is a **Critical - cross-tenant access** issue: an unprivileged internet user (only needing their own free/dev store, no access to the target's credentials or infrastructure) can inject data attributed to a different tenant.

### Likelihood Explanation
Exploitation requires only:
1. Installing the vulnerable app on an attacker-controlled Shopify store (routinely available to anyone via a dev/partner store).
2. Triggering any subscribed webhook topic to obtain a genuine `(raw_body, hmac)` pair from Shopify.
3. Sending that exact body/HMAC directly to the app's public webhook endpoint with a forged `x-shopify-shop-domain` header.

No secrets, tokens, or privileged access are needed — the webhook endpoint is a public HTTP endpoint by design, and the vulnerable code path (`Request` + `HmacValidator` + `Registry.process`) is exactly the one every consuming app uses.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook-id`) into the value that is authenticated, or otherwise cryptographically tie the header to the signed body, e.g., by making `Request#to_signable_string` incorporate the `shop-domain` header (matching how Shopify itself associates the header with the specific delivery), or by requiring consuming apps to cross-check `request.shop` against an independently known/registered shop before trusting it in `WebhookMetadata`. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated relative to the HMAC check and must not be used as the sole tenant-scoping key.

### Proof of Concept
```ruby
# Attacker sets up their own shop "attacker.myshopify.com" running the target app,
# and receives a legitimate webhook delivery for topic "customers/update":
raw_body = '{"id":1,"email":"attacker@evil.com"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), APP_SECRET, raw_body) # genuinely signed by Shopify

# Attacker replays the exact same body+hmac to the app's public webhook endpoint,
# but swaps the shop-domain header to the victim's shop:
headers = {
  "x-shopify-topic" => "customers/update",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",  # <-- forged, not covered by HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) => true (body/hmac pair is valid)
# handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
# The app now processes attacker-controlled data as if it belongs to victim-shop.
```
Confirm root cause: `Request#to_signable_string` at [2](#0-1)  never includes `shop`, so the forged header passes validation in [4](#0-3) .

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
