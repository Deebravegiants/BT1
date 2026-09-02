Confirmed: the HMAC binding gap in the webhook path is real and library-owned.

### Title
Webhook `shop` (and `topic`/`webhook_id`) header is trusted by `Registry.process` without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, `api_version`, and `webhook_id` are read from unauthenticated HTTP headers. `Registry.process` accepts any request whose body+HMAC pair validates against the app's shared `client_secret`, then dispatches to handlers using the header-derived `shop`, without ever binding that value to the HMAC. This lets a party who possesses one valid `(body, hmac)` pair for the app (e.g., a merchant that installed the app and can observe its own genuine webhook deliveries) submit that same pair to the app's public webhook endpoint with an arbitrary `shopify-shop-domain` header, causing the payload to be processed as if it belonged to a different shop.

### Finding Description
- `Request#to_signable_string` binds the HMAC only to `@raw_body`: [1](#0-0) 
- `shop`, `topic`, `api_version`, and `webhook_id` are all sourced from request headers and are never part of the signed material: [2](#0-1) 
- `HmacValidator.validate` verifies only `to_signable_string` (i.e., the body) against `Context.api_secret_key`, which is the same secret for every shop that installs the app: [3](#0-2) 
- `Registry.process` trusts `request.shop` for dispatch immediately after this body-only HMAC check succeeds, with no comparison between the header-derived shop and any signed claim: [4](#0-3) 

The equality the library implicitly assumes is:
`hmac_valid(raw_body) == true` implies `shop_header == actual_originating_shop`

This does not hold, because the HMAC secret (`client_secret`) is shared across every shop that installs a given app, and the signature covers only the body. Any tenant who legitimately receives a webhook for their own shop (thus obtaining a valid `raw_body` + `hmac-sha256` pair) can replay that exact pair to the app's public webhook endpoint while substituting the `shopify-shop-domain` (and optionally `topic`/`webhook-id`) header for a victim shop. `HmacValidator.validate` still returns `true` because it never inspects those headers, and `Registry.process` forwards `WebhookMetadata.new(shop: request.shop, ...)` to the app's handler, cross-attributing the attacker's own payload to the victim tenant.

### Impact Explanation
This is a cross-tenant identity binding break: the field acted upon (`shop`) is never covered by the cryptographic check that is supposed to authenticate the message's origin. An attacker (any merchant able to install the same app - an "unprivileged" party relative to other tenants) can make the host application process attacker-controlled webhook data under a victim shop's identity, without needing the victim's access token, session, or the app's `client_secret`. Depending on how the host app's webhook handlers use `data.shop` (e.g., to look up sessions, write shop-scoped records, or trigger shop-scoped side effects), this enables cross-tenant data corruption or state confusion — matching the Critical "cross-tenant access" category.

### Likelihood Explanation
Exploitation only requires the attacker to be able to install (or otherwise legitimately receive one webhook from) the target application once, which is available to any unprivileged Shopify merchant/developer testing the app, then replay the captured `(raw_body, hmac-sha256)` pair to the app's public webhook endpoint with a forged `shopify-shop-domain` header. No secret material, access token, or victim credentials are required, and the vulnerable code path (`Request`/`HmacValidator`/`Registry.process`) is exercised on every inbound webhook the library processes.

### Recommendation
Include the identity-binding fields (`shop`, `topic`, and ideally `webhook_id`) in the HMAC-signed material, or otherwise cryptographically bind the header-derived shop domain to the signed body before dispatch. At minimum, `Request#to_signable_string` should incorporate the `shop-domain` header alongside the raw body, and `Registry.process` should reject requests where the shop cannot be verified against the signature.

### Proof of Concept
1. Install the target app on Shop A (attacker-controlled) and capture one legitimate webhook delivery: raw body `B` and header `x-shopify-hmac-sha256: H` (valid for `Context.api_secret_key`), plus `x-shopify-shop-domain: shop-a.myshopify.com`.
2. Construct a new HTTP POST to the app's webhook endpoint with the exact same body `B` and `x-shopify-hmac-sha256: H`, but set `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally change `x-shopify-topic`/`x-shopify-webhook-id`, which are also unsigned).
3. `ShopifyAPI::Webhooks::Request.new` parses these headers, and `Registry.process` calls `Utils::HmacValidator.validate(request)`, which returns `true` because it only recomputes the HMAC over `B` — matching `lib/shopify_api/webhooks/request.rb` line 36-38 and `lib/shopify_api/utils/hmac_validator.rb` line 27-31.
4. The handler registered for the (attacker-chosen) topic executes with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)`, as shown in `lib/shopify_api/webhooks/registry.rb` line 198-199, causing the host app to process attacker-supplied data under the victim shop's identity.

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
