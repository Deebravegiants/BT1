Confirmed the root cause. This directly matches the required bug class: a field acted on (`shop`) but not covered by the HMAC.

### Title
Webhook Shop-Domain Header Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then trusts the unauthenticated `x-shopify-shop-domain` header as the tenant identity passed to the host application's handler. Because the HMAC never covers the shop domain, an attacker who can obtain one valid `(body, hmac)` pair can replay it with an arbitrary shop-domain header and have it accepted as a genuine webhook for any tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0)  The `shop` accessor, by contrast, is read directly from the `x-shopify-shop-domain`/`shopify-shop-domain` header, completely outside the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` verifies `verifiable_query.to_signable_string` (i.e. only the body) against `verifiable_query.hmac`: [3](#0-2) 

`Registry.process` uses this same HMAC check as its sole authentication gate, then forwards `request.shop` — the unauthenticated header — straight to the app's webhook handler as the tenant identity: [4](#0-3) 

Binding broken (equality that should hold but doesn't): `shop_bound_by_hmac == shop_delivered_to_handler`. In reality, `shop_verified_by_HMAC = ∅` (HMAC only covers `raw_body`), while `shop_delivered_to_handler = header["x-shopify-shop-domain"]`, an attacker-controlled value.

Exploit path (unprivileged internet user, no `api_secret_key` needed):
1. Attacker installs the target app on their own Shopify development/trial store (a normal, unprivileged action — no special credentials required).
2. Shopify sends the attacker's own store a legitimate webhook (e.g. `orders/create`, `app/uninstalled`) with a valid `x-shopify-hmac-sha256` signature computed by Shopify over the JSON body using the app's real secret — the attacker never needs to know the secret, they just capture this genuine request.
3. Attacker replays the exact same body and HMAC value to the app's webhook endpoint, but substitutes the `x-shopify-shop-domain` header with a victim's `*.myshopify.com` domain.
4. `HmacValidator.validate` still succeeds because it only checks `raw_body` against the (still valid) HMAC — the shop header is never part of the signable string.
5. `Registry.process` calls the app's handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: attacker's JSON, ...)`, and the host application will process/act on this data as if it legitimately originated from the victim shop.

### Impact Explanation
This breaks the tenant-identity binding that webhook consumers rely on to route/attribute events to the correct shop. Any app built on this library that uses `WebhookMetadata#shop` to look up per-tenant records, trigger tenant-scoped side effects, or make authorization decisions (e.g., treating `app/uninstalled` as a signal to revoke access, or `shop/redact` to delete data) can be tricked into performing those actions against an arbitrary victim shop the attacker never had access to. This is a cross-tenant boundary violation caused entirely by this gem's failure to bind the delivery-address header to the cryptographic proof of authenticity.

### Likelihood Explanation
High. The only prerequisite is a single genuine webhook delivery to a store the attacker legitimately controls (trivial — creating a development store and installing the target app is unprivileged and free). No access to `api_secret_key`, access tokens, or any victim credential is required; only the JSON body and header are replayed with one header value changed.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) as part of the HMAC-signed material, or independently verify that the `x-shopify-shop-domain` header corresponds to a shop with an active, known installation/session before trusting it in `WebhookMetadata`. At minimum, document and enforce that `Registry.process` callers must cross-check `request.shop` against an authenticated session/install record rather than treating a successful body HMAC check as proof of shop identity.

### Proof of Concept
```ruby
# Attacker has legitimately received ONE genuine webhook for their own store:
genuine_body = '{"id":1,"note":"hi"}'
genuine_hmac_header = "REAL_BASE64_HMAC_FROM_SHOPIFY_FOR_ATTACKER_SHOP"

# Attacker replays it, swapping only the shop-domain header:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => genuine_hmac_header, # still valid: HMAC only covers body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # unauthenticated, attacker-chosen
  "x-shopify-webhook-id" => "any-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: genuine_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) succeeds (body unchanged)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
# The app now believes this event genuinely originated from victim-shop.myshopify.com.
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
