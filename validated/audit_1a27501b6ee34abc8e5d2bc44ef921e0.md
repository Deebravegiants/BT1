### Title
Webhook shop identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature exclusively over the raw request body, while the `shop` (and `topic`, `webhook_id`, `api_version`) values used to identify the tenant are read directly from unauthenticated HTTP headers. `Registry.process` validates only the HMAC-over-body and then trusts the header-derived `shop` value when dispatching to the app's handler, breaking the intended binding between "HMAC-verified bytes" and "the shop the payload is attributed to."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` (and `topic`/`webhook_id`/`api_version`) are parsed straight from headers with no cryptographic binding to the signature: [2](#0-1) [3](#0-2) 

`HmacValidator.validate` signs/compares against `verifiable_query.to_signable_string` (i.e., only the body) using the app's single `Context.api_secret_key`, which is shared across every shop that has installed the app — it is not shop-specific: [4](#0-3) 

`Registry.process` performs this body-only HMAC check and then immediately constructs `WebhookMetadata` using the *unverified* `request.shop` header value, handing it to the app's handler as the authoritative tenant identifier: [5](#0-4) 

The equality that should hold is: **bytes covered by the HMAC == bytes the handler relies on to identify the tenant (`shop`)**. Here, the HMAC covers only the JSON body, while the tenant-identifying `shop` field is taken from a header outside that signature. Since `api_secret_key` is identical for all shops using the app, any attacker who installs the app on their own shop receives a validly HMAC-signed webhook (body + signature) from Shopify. That attacker can capture the raw body and its valid signature, then replay it against the app's webhook endpoint with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header changed to a victim shop. `Utils::HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` dispatches to the handler with `WebhookMetadata#shop` set to the victim's domain, spoofing the tenant of the webhook payload.

### Impact Explanation
This breaks the tenant boundary the gem is expected to enforce for webhook processing: an unprivileged attacker who is merely a legitimate (even free-tier) merchant of the app can forge/replay a webhook that the app framework will treat as originating from a shop they do not control. Any handler that keys off `WebhookMetadata#shop` to look up sessions, apply mandatory-webhook actions (e.g., `shop/redact`, `customers/redact`, `customers/data_request` — see `MANDATORY_TOPICS`), or write per-tenant state can be tricked into acting on/against another merchant's tenant, i.e., cross-tenant access/confusion facilitated directly by this gem's signature-verification design.

### Likelihood Explanation
Likelihood is High for any host app that trusts `WebhookMetadata#shop` (as the API is documented/intended to be used) without independently re-validating the shop against out-of-band state. The attacker only needs to install the target app on a shop they control (no special privilege, no leaked secret) to obtain a validly signed body+HMAC pair, then replay it with a modified shop header — no `api_secret_key` or access token is required.

### Recommendation
Include the `shop` (and ideally `topic`, `webhook_id`) header values in the signable string checked by the HMAC, or otherwise cryptographically bind them to the payload signature, so `Utils::HmacValidator.validate` fails whenever the shop header does not match the exact one Shopify signed. Short term, document that `WebhookMetadata#shop` must not be trusted as tenant-authoritative unless cross-checked against a known/registered shop for the installation making the request.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives (or triggers) a legitimate webhook, capturing `raw_body` and its `x-shopify-hmac-sha256` value.
2. Attacker resends the identical `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes the HMAC over `raw_body` only [1](#0-0)  and it matches (same body, same app secret), so validation passes.
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)` [6](#0-5) , causing the app to process attacker-controlled payload data as if it belongs to the victim shop.

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
