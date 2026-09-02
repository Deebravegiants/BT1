## Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, so the HMAC verification performed by `ShopifyAPI::Utils::HmacValidator.validate` binds the signature to the body bytes only. The `shop` (from the `shopify-shop-domain`/`x-shopify-shop-domain` header) is read separately and handed to the webhook handler unauthenticated. Because the app's `client_secret` (used to compute the HMAC) is shared across every shop that has the app installed, any tenant that can obtain one validly-signed webhook body can replay it to the app's webhook endpoint with an attacker-chosen `shop-domain` header and have it accepted as coming from a different shop.

### Finding Description
The HMAC validation flow is: [1](#0-0) 

```
def hmac
  Digest.hexencode(Base64.decode64(...))
end
...
def shop
  T.cast(shopify_header("shop-domain"), String)
end
...
def to_signable_string
  @raw_body
end
```

`to_signable_string` (the bytes that get HMAC'd) is `@raw_body` alone — the `shop` header is never mixed into the signable string. Verification is: [2](#0-1) 

`OpenSSL.secure_compare(computed_signature, received_signature)` is computed only over `to_signable_string`, i.e., only over the body.

The registry then trusts `request.shop` (parsed straight from the unauthenticated header) once the body-only HMAC passes: [3](#0-2) 

```
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))
end
```

This breaks the intended identity binding:
`HMAC(client_secret, raw_body) == received_hmac` should imply `(shop, body)` legitimately originated together from Shopify for that specific shop. In reality the equality only proves `body == body-that-was-signed`; `shop` is asserted, not proven, because it is outside the signed byte range.

Since the same app `client_secret` is used to validate webhooks for *every* shop that installs the app, any merchant/tenant of the app (an "unprivileged internet user" relative to other tenants) that legitimately receives one valid `(body, hmac)` pair for their own shop's webhook can:
1. Capture the raw body + `x-shopify-hmac-sha256` value of a webhook Shopify sent for their own shop.
2. Replay the same body/HMAC to the app's public webhook endpoint, substituting `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `HmacValidator.validate` still succeeds because it never inspected the shop header.
4. `Registry.process` calls the handler with `shop: "victim-shop.myshopify.com"` and the attacker-controlled/replayed body, so the host application updates or acts on data keyed to the victim shop using the attacker's payload.

### Impact Explanation
This is a cross-tenant data-integrity bypass: an authenticated-but-unprivileged tenant of a multi-tenant Shopify app can make the app process webhook data under another shop's identity, because the `shop` field acted upon by `Registry.process`/the app's handler is not covered by the HMAC that gates trust. Depending on how the host app uses `WebhookMetadata#shop` (e.g., keying inventory sync, order records, uninstall/GDPR handling per shop), this enables cross-tenant data corruption or spoofed events for shops other than the attacker's own — matching the "Critical: cross-tenant access" impact class.

### Likelihood Explanation
Exploitability requires only capturing/replaying an already-signed webhook body that Shopify sent to the attacker's own store (which the attacker legitimately receives) and reissuing it with a different `shop-domain` header value against the public webhook endpoint. No secret material, no privileged access, and no TLS interception is required — the webhook receiver is a normal internet-reachable endpoint by design.

### Recommendation
Include the `shop` (and ideally `topic`) header value in the bytes that are HMAC-verified, or otherwise cryptographically bind the shop identity to the signed payload, e.g., by having `Request#to_signable_string` concatenate the shop domain and topic with the raw body before computing/comparing the signature, matching what the header actually claims.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com` and `victim-shop.myshopify.com`, both verified with the same `Context.api_secret_key`.
2. Shopify sends a legitimate webhook to the app for `attacker-shop.myshopify.com`: body `B`, header `x-shopify-hmac-sha256: H = HMAC(secret, B)`, header `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures `(B, H)` (e.g., by controlling a local logging proxy in front of their own app instance, or simply having access to their own tenant's webhook deliveries).
4. Attacker sends a new HTTP POST to the app's public webhook endpoint with body `B`, `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses this successfully; `HmacValidator.validate` returns `true` because `to_signable_string` is `B`, unchanged.
6. `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the host app to act on data destined for the attacker's shop as if it belonged to the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
