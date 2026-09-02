Based on my investigation, I've confirmed the finding. Here's the analysis:

### Title
Webhook shop/topic identity is not covered by the HMAC signature, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`, `topic`, `webhook_id`, `api_version`) entirely from HTTP headers, while `Utils::HmacValidator` only authenticates the raw request body. An attacker who can obtain one valid `(body, hmac)` pair for their own shop can replay it to the app's webhook endpoint with a forged `shopify-shop-domain`/`shopify-topic` header, and `HmacValidator.validate` still returns `true`, causing the handler to process the payload under a different tenant's identity.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` values are read straight from headers and are never part of the signed content: [2](#0-1) 

`HmacValidator.validate_signature` computes the signature strictly over `to_signable_string` (the body) and secure-compares it to the header-supplied `hmac`: [3](#0-2) 

`Registry.process` trusts this outcome and forwards the header-derived `shop`/`topic` directly to the app's handler without any cross-check against the signed body: [4](#0-3) 

The identity binding that should hold is: **shop/topic authenticated == shop/topic acted on**. Here, only the body bytes are authenticated; the `shop-domain`/`topic` headers that determine *whose* data the handler acts on are unauthenticated. Any unprivileged internet user can legitimately install a public Shopify app on their own development/test shop (no special privilege required) and receive genuine webhook deliveries for that shop, each with a valid `(body, hmac)` pair signed with the app's `client_secret`. Because the header carrying the target shop identity is excluded from the signature, that same `(body, hmac)` pair remains valid when replayed directly to the app's public webhook endpoint with a different `shopify-shop-domain` header value, causing `HmacValidator.validate` to accept it and the app's handler to attribute/act on that data as if it belonged to a different, arbitrary shop.

### Impact Explanation
This breaks the tenant identity binding at the exact boundary this gem is responsible for enforcing (webhook authenticity). By forging the `shop`/`topic` headers while reusing a validly-signed body, an attacker can inject events attributed to a tenant of their choosing into the app's webhook processing pipeline, e.g. triggering business logic (order updates, `customers/data_request`/`redact` mandatory topics, uninstall flows, etc.) against a victim shop's stored session/data. This matches the Critical "cross-tenant access" impact category since it lets an attacker cause the app to process/act on data under another merchant's identity without ever having credentials for that merchant.

### Likelihood Explanation
Likelihood is moderate-to-high: obtaining a valid `(body, hmac)` pair requires nothing more than installing the target public app on any shop the attacker controls (a normal, unprivileged action), then capturing the outbound webhook (their own traffic) and replaying it to the same public endpoint with a modified `shop-domain`/`topic` header. No knowledge of `client_secret` or access tokens is needed since the HMAC itself is reused verbatim.

### Recommendation
Bind the delivery metadata into the authenticated material: include `shop`, `topic`, and `webhook_id` in `to_signable_string` (mirroring how `Auth::Oauth::AuthQuery#to_signable_string` binds `shop`/`state` into its signed string), or otherwise require the host application to validate that the header-derived `shop` matches a shop for which a webhook was actually expected/registered before invoking the handler. At minimum, document prominently that `WebhookMetadata#shop`/`#topic` are not covered by the HMAC and must not be trusted for tenant-scoping decisions without additional verification.

### Proof of Concept
1. Attacker installs the target public app on `attacker-shop.myshopify.com` (any unprivileged user can do this) and registers a webhook (e.g. `orders/create`).
2. Shopify delivers a webhook to the app's endpoint with body `B` and header `shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)`, and `shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures `(B, H)` from their own delivery (e.g. via a debug proxy on traffic they control) and POSTs it to the same public webhook endpoint, replacing only the header:
   `shopify-shop-domain: victim-shop.myshopify.com`
4. `HmacValidator.validate` recomputes `HMAC-SHA256(client_secret, B)`, which still equals `H`, so validation passes: [5](#0-4) 
5. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` with `shop == "victim-shop.myshopify.com"`, so the app's business logic executes as if `victim-shop` sent this webhook payload.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
