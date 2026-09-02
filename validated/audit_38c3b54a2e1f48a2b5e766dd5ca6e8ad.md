## Finding

The webhook signature verification in this gem authenticates the request body but never binds that signature to the `shop` identity that the SDK reports to the application's webhook handler. This breaks the identity binding: `HMAC-verified bytes == raw_body` while `shop attribution used by the app == unauthenticated header value`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Title
Webhook shop attribution is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, and `ShopifyAPI::Utils::HmacValidator.validate` checks the HMAC solely against that body. The `shop` value passed to the developer's webhook handler is read straight from the `x-shopify-shop-domain` / `shopify-shop-domain` header, which is never part of the signed content. Because a single app-level `api_secret_key` (the app's client secret) is used to sign webhooks for *every* shop that installs the app, anyone who installs the app on their own store receives a validly-HMAC-signed `(body, hmac)` pair. That exact pair can be replayed to the app's webhook endpoint with the `shop-domain` header swapped to a victim shop, and `HmacValidator.validate` will still return `true` because it never inspects the header.

### Finding Description
- `HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it with the request's `hmac` value via `OpenSSL.secure_compare`. [5](#0-4)  For `Webhooks::Request`, `to_signable_string` is just `@raw_body`. [2](#0-1) 
- `Request#shop` is derived purely from an HTTP header with no cryptographic tie to the body or hmac. [6](#0-5) 
- `Registry.process` only checks `Utils::HmacValidator.validate(request)` before dispatching to the handler with `shop: request.shop` taken from that unauthenticated header. [4](#0-3) 
- Since all shops sharing one app use the same `api_secret_key` for webhook signing (the same secret validated in `HmacValidator`), a body legitimately signed for shop A's install still produces a valid signature no matter what `shop-domain` header accompanies it. The library provides no mechanism (e.g., binding shop into the signed payload, or requiring out-of-band shop verification) to prevent this substitution.

Equality broken: `bytes verified by HMAC (raw_body)` ≠ `identity (shop) acted upon by the handler (header value)`.

### Impact Explanation
This is a cross-tenant access issue (High/Critical class per the assignment's impact list): an attacker who installs the target app on any shop they control (including a free Shopify dev/partner store) can force the app to process a webhook body as if it originated from an arbitrary victim shop domain, because the SDK's HMAC check gives no assurance about `shop` attribution. Depending on how the host app uses `data.shop` (e.g., GDPR "customers/data_request" processing, "app/uninstalled" cleanup, order/customer sync keyed by shop), this can lead to cross-tenant data corruption, spurious uninstall/cleanup actions against another merchant's data, or injection of attacker-controlled payload content attributed to a victim tenant.

### Likelihood Explanation
Practical: an attacker only needs a free/dev Shopify store to install the target public app and capture one legitimate webhook (body + `x-shopify-hmac-sha256`), then replay it to the same public webhook endpoint with the `x-shopify-shop-domain` header changed. No access to `api_secret_key`, tokens, or TLS interception is required — the attacker uses their own legitimately-received, validly-signed webhook.

### Recommendation
Bind the shop identity into the value that `HmacValidator` verifies (e.g., include `shop-domain` and other identifying headers/claims in `to_signable_string` for `Webhooks::Request`, or otherwise cryptographically tie the reported `shop` to the signed payload) so replaying a valid signature with a different `shop-domain` header is rejected.

### Proof of Concept
1. Attacker creates a free development store and installs the target public app; the app registers a webhook (e.g. `app/uninstalled`) at `https://target-app.example.com/webhooks`.
2. Shopify sends a legitimate request: body `B`, header `x-shopify-hmac-sha256: H` (valid for secret `S`, the app's shared `api_secret_key`), and `x-shopify-shop-domain: attacker-store.myshopify.com`.
3. Attacker replays the exact same request to the same endpoint, keeping body `B` and header `H` unchanged, but sets `x-shopify-shop-domain: victim-store.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, B) == H` — still true — and dispatches the handler with `shop: "victim-store.myshopify.com"`, `body: B`. [4](#0-3) 
5. The host application performs shop-scoped side effects (e.g., uninstall cleanup, GDPR deletion) against `victim-store.myshopify.com` using attacker-controlled `B`.

### Citations

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
