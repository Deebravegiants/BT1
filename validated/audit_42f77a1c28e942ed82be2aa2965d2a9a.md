### Title
Webhook shop-domain header is trusted by handlers but not covered by the HMAC signature, enabling cross-tenant impersonation - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` for webhook HMAC verification, but its `to_signable_string` only returns the raw HTTP body [1](#0-0) . The `shop` (and `topic`, `api_version`, `webhook_id`) values are read straight from attacker-controllable HTTP headers and are never part of what is HMAC-verified [2](#0-1) . `Registry.process` validates the HMAC and then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler [3](#0-2) . This is the same class of bug as the reported analog: a value that is acted upon (the "winner"/destination) is not bound by the verification that is supposed to authorize the action (the reward-swap trigger only checks the moved amount, not who receives it).

### Finding Description
The equality that should hold is:
`shop authenticated by HMAC == shop acted upon by the webhook handler`

In `Request#to_signable_string`, only `@raw_body` is signed:
```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

`shop` is a plain header read with no cryptographic binding to the signature:
```ruby
sig { returns(String) }
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [4](#0-3) 

`HmacValidator.validate` computes the HMAC over `to_signable_string` (the body only) and compares it to the received signature — it has no visibility into the `shop` header at all [5](#0-4) .

`Registry.process` gates on this HMAC check, then forwards the unauthenticated `request.shop` value straight to the app's handler:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [3](#0-2) 

An unprivileged internet user who legitimately installs the app on their own shop (or otherwise obtains one genuine `(raw_body, hmac)` pair from Shopify — since `hmac-sha256` computation depends only on the body, not on shop, any body/hmac pair is portable across shops) can replay that exact body and HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for any victim shop. `Registry.process` and the library's own HMAC check will pass unmodified, and the handler will be invoked with `WebhookMetadata#shop` set to the attacker-chosen victim domain, causing it to treat the payload as authoritative data for the impersonated tenant.

### Impact Explanation
This is a cross-tenant identity binding break at the library layer that this gem's own `Registry.process`/`Request` code owns: it verifies "the body is untampered from *a* legitimately-HMAC'd Shopify payload" but presents `shop` to consuming code as if it were equally verified, when it is not bound at all. Any host application that keys per-shop logic (e.g. `shop/redact`, `app/uninstalled`, data sync, entitlement changes) off `WebhookMetadata#shop` as returned by this gem can be made to act on behalf of, or against, a shop the attacker does not own — a cross-tenant access impact.

### Likelihood Explanation
Reaching this requires only: (1) the attacker to install the app on any shop they control (unprivileged, ordinary merchant action) to receive at least one real Shopify webhook delivery with a legitimate `(body, hmac)` pair, then (2) replaying that raw request to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain`/`shopify-shop-domain` header. No access token, `client_secret`, or privileged account is needed — the library itself never checks the header against the signature.

### Recommendation
Include the `shop` (and ideally `topic`/`api-version`/`webhook-id`) header values in the signable string used for HMAC validation, or otherwise separately verify/bind the `shop-domain` header to the registered destination for that webhook subscription before constructing `WebhookMetadata`. At minimum, document and enforce that `request.shop` must not be trusted as authenticated unless independently corroborated (e.g., cross-checked against the shop associated with the specific webhook/topic subscription record).

### Proof of Concept
1. Attacker installs the app on their own store `attacker-shop.myshopify.com` and triggers any registered webhook topic (e.g. `orders/create`), capturing the exact raw request body `B` and the `X-Shopify-Hmac-Sha256` header `H` that Shopify sent for that delivery.
2. Attacker sends a POST to the app's webhook endpoint with body `B` unchanged, header `X-Shopify-Hmac-Sha256: H` unchanged, but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is constructed; `to_signable_string` returns `B` [1](#0-0) .
4. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` and matches `H` — validation succeeds even though the shop header was changed [6](#0-5) .
5. The registered handler is invoked with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)`, causing the app to process the attacker's payload as if it belonged to the victim shop [7](#0-6) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
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
