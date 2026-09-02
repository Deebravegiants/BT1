### Title
Webhook processing trusts the unauthenticated `shop-domain` header while HMAC only covers the raw body, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` extracts `shop` from the `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header, but `to_signable_string` (which is what `Utils::HmacValidator` verifies against the HMAC) only ever includes the raw request body. The tenant-identifying field (`shop`) that the host application relies on to attribute the event is never covered by the cryptographic check, breaking the equality that should hold: `hmac_verified_bytes == bytes_used_to_derive_tenant_identity`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . `shop` is read straight from an HTTP header without any binding to the HMAC: [2](#0-1) .

`ShopifyAPI::Webhooks::Registry.process` verifies the HMAC via `Utils::HmacValidator.validate(request)` and, on success, immediately forwards `request.shop` to the handler as the tenant identity, with no further check that this header value is consistent with anything cryptographically verified: [3](#0-2) .

`Utils::HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (i.e., the raw body for webhooks) and compares it to the `hmac` field, never touching `shop`: [4](#0-3) .

Because the app's `api_secret_key` is shared across every shop that installs the app (it is not per-shop), any two webhook deliveries — even ones destined for two completely different merchants — are signed with the exact same secret and validate against the exact same signable string when the raw body is identical or attacker-controlled. An attacker who legitimately installs the target app on their own shop (an ordinary, unprivileged action available to anyone with a Shopify Partner/dev account) will receive real webhook deliveries with valid `(raw_body, hmac)` pairs signed with the app's secret. Nothing prevents them from replaying that exact `(raw_body, hmac)` pair to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` then calls the handler with `WebhookMetadata.new(shop: request.shop, ...)` where `shop` is the attacker-controlled value, not something proven by the signature.

This is the direct analog of the report's bug class: a field that is acted upon (here, `shop`, used by the host app to key sessions/data per tenant) is not covered by the identity-binding check (here, the HMAC), so `shop_used_for_tenant_attribution != shop_actually_authenticated_by_hmac`.

### Impact Explanation
Host applications built on this gem are expected to trust `WebhookMetadata#shop` as the authoritative tenant identifier for a webhook event (per the gem's public API surface, `Registry.process` hands this value straight to the handler). Because the shop cannot be forged-detected by the gem, an attacker can cause the app to process arbitrary attacker-supplied webhook bodies under a victim shop's identity. Depending on which webhook topics the app registers (e.g. `app/uninstalled`, `shop/redact`, `customers/data_request`, `shop/update`), this enables cross-tenant data corruption, deletion of a victim's stored session/access token, or forced state changes attributed to a shop the attacker does not control — a cross-tenant integrity/confidentiality violation.

### Likelihood Explanation
Requires only: (1) installing the target app on an attacker-controlled shop (free, self-service, "unprivileged internet user" action), (2) capturing one legitimate webhook delivery from that installation, and (3) POSTing the same body/HMAC pair to the app's public webhook endpoint with a different `shop-domain` header. No access to `api_secret_key`, tokens, or the victim's credentials is needed. This is a low-effort, repeatable attack path.

### Recommendation
Do not treat the `shop-domain` header as trusted tenant identity purely because the body HMAC validates. Either (a) include the shop domain in the signable string used for HMAC computation/verification (requires alignment with Shopify's actual webhook signing scheme, which currently only signs the body — so this may not be feasible unilaterally), or (b) require host applications to cross-check `request.shop` against an independently known/registered shop (e.g., confirm the shop has an active session/webhook registration before trusting the attribution), and document this requirement prominently, or (c) bind webhook idempotency/shop checks against the `webhook_id` returned from Shopify's own systems rather than trusting the header value alone.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" and has installed the target app,
# so Shopify sends them a legitimately-signed webhook using the app's api_secret_key.
raw_body = '{"id":123}'
valid_hmac = Base64.encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)
)

# Attacker replays the exact same body+hmac, but swaps the shop-domain header
# to a victim shop they do NOT control.
spoofed_headers = {
  "x-shopify-topic" => "app/uninstalled",
  "x-shopify-hmac-sha256" => valid_hmac,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled, unverified
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: spoofed_headers)

# HMAC validation succeeds because it only checks raw_body, not shop-domain:
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

# Registry.process forwards the unverified shop to the handler as if it were victim-shop:
ShopifyAPI::Webhooks::Registry.process(request)
# handler receives WebhookMetadata(shop: "victim-shop.myshopify.com", topic: "app/uninstalled", ...)
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
