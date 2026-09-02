### Title
Webhook `shop` domain is not covered by the HMAC signature, allowing cross-tenant webhook spoofing via replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from an HTTP header that is completely outside the byte range covered by the HMAC signature check. `Registry.process` trusts this unauthenticated `shop` value and hands it straight to the app's webhook handler, so any attacker who can replay (or otherwise submit) a body+HMAC pair that once validated for shop A can resubmit it while claiming to be shop B, and the gem will accept it as authentic.

### Finding Description
`Request#to_signable_string` only returns the raw request body: [1](#0-0) 

`Request#shop` is read from the `x-shopify-shop-domain`/`shopify-shop-domain` header, which is disjoint data not fed into the signature computation: [2](#0-1) 

`HmacValidator.validate` only recomputes the HMAC over `verifiable_query.to_signable_string` (the body) and compares it to the `hmac` header — it never incorporates `shop`, `topic`, or any other header: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately forwards the unauthenticated `request.shop` (along with `topic`, `body`, etc.) to the app's handler as if it were verified: [4](#0-3) 

The binding that should hold is:
`shop_bytes_covered_by_HMAC == shop_value_delivered_to_handler`

but in reality:
`shop_bytes_covered_by_HMAC = ∅ (only raw_body is signed)` while `shop_value_delivered_to_handler = header("shop-domain")`

Since these are not the same bytes, the HMAC check proves only "this body byte-string was produced with knowledge of `api_secret_key`" — it proves nothing about which shop the header claims to be. An attacker who obtains one valid `(raw_body, hmac)` pair (e.g., by capturing/replaying a webhook delivery sent to a publicly reachable endpoint, or via a body that is naturally identical/predictable across shops, such as a mandatory `shop/redact` payload with attacker-controlled or shared structure) can resend the exact same bytes while substituting a different `x-shopify-shop-domain` header. `HmacValidator.validate` will still pass because it never looks at the header, and `Registry.process` will call the handler with `shop: <attacker-chosen shop>`. Any app that keys its per-tenant state, session lookup, or data mutation off `WebhookMetadata#shop` (the officially documented field for this exact purpose) will act on the wrong tenant.

### Impact Explanation
This breaks the tenant-identity boundary the HMAC check is supposed to establish: a request nominally "verified for shop A" can be relabeled as belonging to shop B without knowledge of `api_secret_key`. Applications built on this gem are expected to trust `WebhookMetadata#shop`/`#topic` once `Registry.process` succeeds; because that trust is misplaced, an attacker can cause cross-tenant state changes (e.g., trigger uninstall/redact flows, or any handler logic keyed on shop) for a shop they don't control. This matches the Critical category of cross-tenant access.

### Likelihood Explanation
Exploitation requires the attacker to obtain at least one legitimate `(raw_body, hmac)` pair for the topic they want to abuse (e.g., via network capture of a webhook delivered over an app's public endpoint, a shared/predictable payload topic, or a previously-seen webhook from their own shop) and then replay it with an arbitrary `shop-domain` header value against the same endpoint. No possession of `api_secret_key` or an access token is required, and no interception of TLS is required beyond what is needed to observe traffic destined for the app's own public webhook endpoint (which is the normal channel Shopify itself uses).

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, `webhook-id`) in the HMAC-covered signable string, or otherwise cryptographically bind `shop` to the signed payload, matching how the OAuth `AuthQuery` signable string binds the parameters it authenticates. At minimum, document that `request.shop` is unauthenticated and must be cross-checked by the application against a known/installed shop list before being trusted for any tenant-scoped operation.

### Proof of Concept
```ruby
# 1. Attacker observes/receives one legitimate webhook delivery for their own shop:
#    body = raw_body_bytes
#    valid_hmac = header["x-shopify-hmac-sha256"]  (computed by Shopify over raw_body only)

# 2. Attacker resends the identical body+hmac to the app's webhook endpoint,
#    but swaps the shop-domain header to a victim shop:
headers = {
  "x-shopify-topic" => "shop/redact",
  "x-shopify-hmac-sha256" => valid_hmac,          # unchanged, still valid because only body is signed
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",  # forged
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: headers)

# 3. HmacValidator.validate only checks body vs valid_hmac -> passes
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "shop/redact", ...))
# The app's handler now acts on victim-shop's data despite the HMAC never having authenticated
# that "victim-shop.myshopify.com" is the shop associated with this payload.
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
