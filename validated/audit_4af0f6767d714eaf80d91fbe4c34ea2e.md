## Title
Webhook `shop` identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw JSON body only, while the `shop` identity that gets handed to the application's webhook handler is read from an HTTP header that is never covered by that HMAC. Any actor who can obtain one genuine, correctly-signed webhook (e.g. by installing the app on their own store) can replay that exact body/HMAC pair while substituting a different `shop-domain` header, and the registry will accept it as a validly-authenticated webhook "from" the victim shop.

### Finding Description
`Utils::HmacValidator.validate` verifies a signature over `verifiable_query.to_signable_string` and compares it against `verifiable_query.hmac`: [1](#0-0) 

For webhooks, `Request#to_signable_string` returns only `@raw_body`, while `Request#hmac` and `Request#shop` are both pulled independently from headers: [2](#0-1) [3](#0-2) 

`Registry.process` performs the HMAC check and then unconditionally trusts `request.shop` when constructing the data passed to the application's handler: [4](#0-3) 

This is the exact bug-class from the report: a value that is *acted upon* (here, the tenant identity `shop`) is not part of the data that is *cryptographically bound* (the HMAC only signs `@raw_body`). The equality the code implicitly assumes — `shop-header == the shop the HMAC actually attests to` — does not hold, because the header is entirely outside the signed payload.

**Before attacker's request:** a genuine webhook for Shop A arrives with `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-hmac-sha256: HMAC(secret, body)`, and body `B`. HMAC validates because it is computed only over `B`.

**Attacker's request sequence:** the attacker (who legitimately installed the app on their own store, Shop A) captures this real webhook. They resend the identical body `B` and identical HMAC header, but replace `x-shopify-shop-domain` with `shop-victim.myshopify.com`.

**After attacker's request:** `HmacValidator.validate` still succeeds (same body, same secret, same signature). `Registry.process` reads `request.shop` from the attacker-controlled header and passes `shop: "shop-victim.myshopify.com"` to the app's `WebhookHandler`, which trusts it as an authenticated statement from Shopify about Shop A's data/event pretending to be Shop B's.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook processing: an app receiving what it believes is an authenticated event for tenant B is actually driven by attacker-controlled tenant-A data. Depending on how the host application keys its per-shop state off `WebhookMetadata#shop` (very common — e.g. to look up/update the record for a shop, trigger uninstall cleanup, or mark subscription state), this can cause cross-tenant data corruption or state confusion for a shop the attacker does not control, which maps to the "cross-tenant access" Critical-impact bucket.

### Likelihood Explanation
The only prerequisite is being a normal, unprivileged app installer for any one shop (self-service, no special access) — from which any webhook the app registers (e.g. `app/uninstalled`, `orders/create`) can be captured and replayed with a rewritten `shop-domain` header. No secret material, access token, or elevated privilege is required, and the gem accepts the header value without any correlation to the signed payload.

### Recommendation
Bind the identity used to route/label webhook processing to the signed payload, not to an unauthenticated header:
- Include the `shop-domain` (and ideally `topic`, `api-version`, `webhook-id`) in the value that is HMAC-verified, or
- Require the host application-configured shop/topic mapping to be validated against the request body content it actually receives (where available), and clearly document that `shop-domain` is not currently bound by the signature so any caller doing per-shop authorization off `WebhookMetadata#shop` must not treat it as attacker-proof without additional verification (e.g. cross-checking against a known/registered shop list rather than blind trust).

### Proof of Concept
```ruby
# 1. Attacker installs the target app on their own store "shop-a.myshopify.com"
#    and receives a real webhook, e.g. for "app/uninstalled":
raw_body = '{"id":123}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)

genuine_headers = {
  "x-shopify-topic" => "app/uninstalled",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "shop-a.myshopify.com",
}

# 2. Attacker replays the identical body/HMAC but swaps the shop-domain header
forged_headers = genuine_headers.merge("x-shopify-shop-domain" => "shop-victim.myshopify.com")

forged_request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# 3. HMAC validation still passes (only body is signed) ...
ShopifyAPI::Utils::HmacValidator.validate(forged_request) # => true

# 4. ... and the handler is invoked believing this is an authenticated event for shop-victim
ShopifyAPI::Webhooks::Registry.process(forged_request)
# handler.handle receives WebhookMetadata(shop: "shop-victim.myshopify.com", ...)
```

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
