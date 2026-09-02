This confirms the finding. The `Registry.process` method validates the HMAC over only the raw body (`Request#to_signable_string` returns `@raw_body`), then passes `request.shop` (parsed from the unauthenticated `X-Shopify-Shop-Domain` header) directly into `WebhookMetadata` for the app's handler to act on tenant-scoped logic.

### Title
Webhook `shop` field is not covered by HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` value from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature validated by `Utils::HmacValidator` only covers the raw request body, not this header. Since the app's `client_secret`/`api_secret_key` is a single shared secret used to validate webhooks for *all* installed shops (not a per-shop secret), any party capable of producing one valid `(raw_body, hmac)` pair for their own shop's webhook can reuse that same pair while substituting an arbitrary `shop-domain` header, and the request will still pass HMAC validation — but be attributed to a different, victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from an unauthenticated header and is never included in the signable string: [2](#0-1) 

`Registry.process` validates the HMAC over the request (i.e., the raw body only) and, if it passes, immediately trusts `request.shop` to construct the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

This breaks the identity binding: `HMAC-verified bytes == raw_body` but `shop used by handler == unauthenticated header`. The equality the code implicitly assumes — "the shop whose webhook secret validated this payload" equals "the shop named in the `shop-domain` header" — does not hold, because the HMAC secret (`Context.api_secret_key`) is shared across all shops that installed the app, not scoped per shop. Any tenant of the app can capture a legitimately-signed `(body, hmac)` pair from their own webhook traffic and replay it with a forged `shop-domain` header naming a different tenant; `HmacValidator.validate` in [4](#0-3)  will still succeed because it never inspects the header.

### Impact Explanation
This matches the report's "Critical" pattern of an unprivileged actor manipulating an input that a downstream computation trusts without adequate binding — here, the trust boundary is which shop the webhook payload actually pertains to. If a host application uses `WebhookMetadata#shop` for tenant-scoped actions (looking up an offline session/access token for that shop, updating per-shop billing/subscription state, deleting or redacting per-shop data on mandatory `shop/redact`-style topics, etc.), an app-installed shop can spoof events as coming from a different shop, resulting in cross-tenant data manipulation using the victim's stored session/access token.

### Likelihood Explanation
Requires the attacker to be able to trigger at least one legitimate webhook delivery to their own shop (trivial — any merchant installing the app receives webhooks) and to be able to POST a custom `shop-domain` header value to the app's webhook endpoint with the captured raw body and HMAC unchanged. No knowledge of `api_secret_key` is needed since the same signed bytes are being replayed verbatim.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the HMAC-covered content, or independently verify that the `shop-domain` header matches a shop for which the raw body's HMAC was expected, before trusting `request.shop` for any tenant-scoped operation. At minimum, document that consumers of `WebhookMetadata#shop` must not treat it as fully authenticated without additional binding.

### Proof of Concept
1. App is installed on `shop-a.myshopify.com`. Shopify sends a legitimate webhook: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid for secret `S`), header `X-Shopify-Shop-Domain: shop-a.myshopify.com`.
2. Attacker (merchant/operator of `shop-a`) captures `(B, H)`.
3. Attacker crafts a new HTTP request to the same webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged), but `X-Shopify-Shop-Domain: shop-b.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(S, B) == H` — this still passes.
5. The handler receives `WebhookMetadata.new(shop: "shop-b.myshopify.com", ...)` and performs shop-b-scoped actions driven by attacker-controlled body `B`, even though shop-b never sent this webhook.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
