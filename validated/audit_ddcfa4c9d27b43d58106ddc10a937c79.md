## Analysis

The strongest analog to the `hasSignedDocs` bug class — a value that downstream code treats as authenticated/verified when it was never actually bound to the cryptographic check that "authenticates" the request — exists in this gem's webhook processing path.

### Root cause

`ShopifyAPI::Webhooks::Request#to_signable_string` returns **only the raw request body**: [1](#0-0) 

`shop`, `topic`, and `webhook_id` are all read directly from unauthenticated HTTP headers, independent of the signable string: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which HMACs `to_signable_string` (i.e. only the body) against `Context.api_secret_key`, then immediately trusts `request.shop` to build `WebhookMetadata` handed to the app's handler: [3](#0-2) [4](#0-3) 

### Why this breaks an identity binding

Shopify signs webhook payloads with the **app's** `client_secret` (`api_secret_key`), which is the same across every shop that installs the app — it is not a per-shop secret. Because `to_signable_string` covers only the JSON body and not the `shopify-shop-domain` header, the HMAC check answers "was this body signed by an app-secret holder" but is asserted by the code to mean "did this body come from shop X." Those are not equal:

`hmac_valid(body, api_secret_key) == true` ⇏ `request.shop == actual_originating_shop`

A user who legitimately receives one genuine webhook for their own shop (a normal, unprivileged merchant/store owner with the app installed) possesses a valid `(body, hmac)` pair. They can replay that exact body and HMAC header to the app's single shared webhook endpoint while forging the `x-shopify-shop-domain` header to name a different, victim shop. `HmacValidator.validate` still passes (it never looks at the shop header), so `Registry.process` calls the handler with `WebhookMetadata.shop` set to the attacker-chosen victim shop, even though the payload never originated from Shopify for that shop.

### Impact

Any app handler that uses `WebhookMetadata#shop` to select which tenant record to update (a standard pattern, e.g. updating order/inventory state "for this shop") can have another shop's real data injected/attributed to a victim shop, or have a victim shop's webhook processing spoofed by an attacker who merely has their own legitimate webhook traffic to replay. This is a cross-tenant integrity/confidentiality break driven purely by the library's HMAC/identity binding gap — no leaked secrets or privileged access are required, only observing one's own legitimate webhook call.

### Title
Webhook shop/topic/id fields are not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs/verifies only the raw body, while `shop`, `topic`, and `webhook_id` are read from unauthenticated headers and trusted downstream without being part of the HMAC-protected data.

### Finding Description
`Utils::HmacValidator.validate` proves the body was HMAC'd with the app-wide `api_secret_key`, not that the specific `shop-domain` header is authentic, because `Request#to_signable_string` returns `@raw_body` only [5](#0-4) . `Registry.process` performs the HMAC check and then unconditionally forwards `request.shop` (and `topic`, `webhook_id`) into `WebhookMetadata` passed to the app handler [6](#0-5) . Since the app secret is shared across all shops of an app, any shop's genuine `(body, hmac)` pair remains valid when replayed with a different, forged `shop-domain` header.

### Impact Explanation
This is a cross-tenant identity binding break: the value that determines "which shop this webhook is for" is never authenticated by the cryptographic check the library performs, yet the library's own API (`WebhookMetadata#shop`) is presented to consuming apps as if it were trustworthy/authenticated data.

### Likelihood Explanation
Exploitation requires only capturing one legitimate webhook (body + `hmac-sha256` header) that any installed shop naturally receives, then resending it to the shared webhook endpoint with a modified `shop-domain` header — no access to `api_secret_key`, tokens, or privileged accounts is needed.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (or otherwise cryptographically bind them) in `to_signable_string`, or independently verify the claimed shop domain against the shop that actually owns the webhook subscription/delivery before trusting `WebhookMetadata#shop` in `Registry.process`.

### Proof of Concept
1. App receives a legitimate webhook for `shop-a.myshopify.com`: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's `api_secret_key`).
2. Attacker (an unprivileged user with access to shop A's webhook delivery, e.g. via a proxy/logging tool they control) resends the same `POST` to the app's webhook endpoint, keeping body `B` and header `H`, but sets `x-shopify-shop-domain: shop-b.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H` [7](#0-6) .
4. The handler receives `WebhookMetadata.new(... shop: "shop-b.myshopify.com" ...)` and processes body `B` as if it came from shop B, even though it never did.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-21)
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
