### Title
Webhook `shop-domain` (and topic/webhook-id/api-version) headers are not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw HTTP body for HMAC verification, while the `shop`, `topic`, `webhook_id`, and `api_version` values used downstream by the app's webhook handler are taken from unauthenticated headers that are never included in the signed payload. An attacker who can obtain one genuine, validly-signed webhook body/HMAC pair (e.g., by installing the app on their own store and receiving a webhook Shopify sends them) can replay that exact body and HMAC to the app's public webhook endpoint while forging the `x-shopify-shop-domain` header to claim it belongs to a different, victim shop. Because the HMAC check never covers that header, the tampered request still validates successfully.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all pulled directly from HTTP headers, none of which are part of the signed content: [2](#0-1) 

`HmacValidator.validate` computes the HMAC purely from `to_signable_string` (i.e. the body) and compares it to the `hmac` header value: [3](#0-2) 

`Registry.process` validates the HMAC and then trusts `request.shop` (along with `request.topic`, `request.webhook_id`) to build the `WebhookMetadata` object passed straight to the app's handler, with no separate binding check that the header-derived `shop` actually corresponds to the body that was signed: [4](#0-3) 

This breaks the intended identity binding: `hmac == HMAC(secret, body)` should imply `shop == the tenant that produced body`, but in this implementation `shop` is a free header value carried alongside the signed body rather than an attribute bound into the signature. An attacker satisfies `hmac == HMAC(secret, body)` using a body/HMAC pair legitimately issued to their own shop, then swaps only the `shop-domain` header to any victim shop domain — the equality the code actually verifies (`hmac` matches `body`) still holds, even though the equality the app relies on (`shop` matches the tenant that produced `body`) is now false.

### Impact Explanation
Any app handler logic keyed on `WebhookMetadata#shop` — for example the mandatory compliance topics `shop/redact`, `customers/redact`, `customers/data_request` [5](#0-4) , or handlers that look up/mutate per-shop data using `data.shop` as the tenant key — can be tricked into acting on behalf of, or against, a shop the attacker does not control. This is a cross-tenant confusion/spoofing primitive reachable by an unprivileged internet user who only needs their own (attacker-owned) shop installation to harvest one valid signed webhook, without ever needing the app's `client_secret` or a leaked access token.

### Likelihood Explanation
Webhook endpoints exposed by apps built on this gem are public HTTP endpoints reachable directly by any internet user; no interception or credential theft is required, only ordinary use of the attacker's own shop to generate one legitimate webhook to replay with a substituted `shop-domain` header. The bug is a structural gap in `Request`/`Registry`, not a misuse of a documented API.

### Recommendation
Bind the shop identity into the verified signature material, or otherwise cryptographically tie the `shop-domain` header to the request that produced the HMAC (e.g., require verification that the header matches a shop value embedded in/derivable from the signed body, or document/require callers to independently confirm the requesting shop is one they have on record as installed with a matching webhook subscription id before trusting `WebhookMetadata#shop`). At minimum, this trust boundary should be explicitly documented so integrators do not rely on `request.shop` as an authenticated tenant identifier.

### Proof of Concept
1. Attacker installs the target app on an attacker-controlled development store `attacker-shop.myshopify.com` and triggers a webhook topic the app registers, e.g. `orders/create`.
2. Shopify sends the app: `raw_body = B`, header `x-shopify-hmac-sha256 = HMAC(secret, B)`, header `x-shopify-shop-domain = attacker-shop.myshopify.com`.
3. Attacker resends this exact `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but replaces `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` succeeds because it only checks `HMAC(secret, raw_body)` against the header value — both unchanged from step 2.
5. `Registry.process` builds `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)` and invokes the app handler as if the event originated from `victim-shop.myshopify.com`, even though the payload actually describes attacker-shop's data.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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

**File:** lib/shopify_api/webhooks/registry.rb (L8-12)
```ruby
      MANDATORY_TOPICS = T.let([
        "shop/redact",
        "customers/redact",
        "customers/data_request",
      ].freeze, T::Array[String])
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
