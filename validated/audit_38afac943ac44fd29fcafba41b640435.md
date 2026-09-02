### Title
Webhook shop/topic/webhook-id identity headers are not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by verifying the HMAC over the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` values that identify *which tenant* the webhook belongs to are read from HTTP headers that are never included in the signed material, so they are handed to the host application's handler completely unauthenticated.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) 

`to_signable_string` returns only `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from HTTP headers (`shopify_header`) that are outside the signed payload.

`Registry.process` performs the only authenticity check via `Utils::HmacValidator.validate(request)`, then immediately trusts `request.shop`/`request.topic`/etc. to build the `WebhookMetadata` passed to the app's handler: [2](#0-1) 

`HmacValidator.validate` computes an HMAC over `verifiable_query.to_signable_string` (i.e. the raw body only) and compares it to the header-supplied `hmac`: [3](#0-2) 

The identity binding that should hold is: `shop used to authorize/attribute the webhook == shop that was covered by the HMAC signature`. In this implementation that equality is never enforced — the HMAC only proves the *body bytes* were signed with the app's secret; it says nothing about which shop, topic, or webhook id the signer intended. The documented usage confirms `data.shop` is meant to be trusted as "The shop domain of the webhook" by the handler: [4](#0-3) 

Because any party who has ever received one legitimate webhook delivery for their own shop (e.g. by installing the app on a store they control) possesses a valid `(raw_body, hmac)` pair signed with the app's real secret, they can replay that exact body+HMAC to the app's public webhook endpoint while freely rewriting the `shopify-shop-domain` (and `shopify-topic`/`shopify-webhook-id`) headers to name a different, victim shop. `Utils::HmacValidator.validate` will still succeed because it only checks the body, and `Registry.process` will hand the forged `shop` value straight to the app's handler.

### Impact Explanation
This breaks the tenant boundary the whole webhook mechanism is supposed to enforce: an unprivileged internet user who merely has (or once had) a legitimate installation of the target app on any shop can cause the app to process attacker-supplied webhook content under an arbitrary victim shop's identity. Depending on how the host app uses `data.shop` (looking up the merchant's session/access token, writing records keyed by shop, triggering per-shop business logic), this enables cross-tenant data corruption/injection — an attacker's crafted "order/customer/product" payload gets attributed to and processed for a shop they don't control. This matches the Critical "cross-tenant access" category.

### Likelihood Explanation
The precondition is minimal and requires no secrets: the attacker only needs to have received one webhook of any topic for a shop they control (trivial — anyone can install a public app on a development/trial store) to obtain a valid `(body, hmac)` pair, then send a normal unauthenticated HTTP POST to the app's public webhook route with a different `shop-domain` header. No access to `client_secret`, tokens, or TLS interception is required, and the exposed webhook endpoint is by design public/unauthenticated apart from this HMAC check.

### Recommendation
Bind the shop (and ideally topic/webhook id) identity into the value that is actually authenticated, rather than trusting header values wholesale:
- Reject the webhook unless `request.shop` matches a shop for which the app currently holds a valid session/access token (cross-check against stored sessions before invoking the handler), and/or
- Have `Registry.process` require the caller to supply the expected shop (from the route/session context) and compare it against `request.shop`, refusing to proceed if they differ, and/or
- Where possible, include the `shop-domain`/`topic`/`webhook-id` header values in the signed material used by `to_signable_string` so `HmacValidator` actually covers them.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers any webhook (e.g. `orders/create`) to their own registered callback URL, capturing the raw POST body and the `X-Shopify-Hmac-Sha256` header value Shopify sent — both are valid because they were legitimately signed by Shopify with the app's real secret for the attacker's own shop.
2. Attacker sends a new HTTP POST directly to the same app's public webhook endpoint, reusing the exact captured `raw_body` and `hmac` header, but rewrites the `shopify-shop-domain` header to `victim-shop.myshopify.com` (and optionally `shopify-topic`/`shopify-webhook-id`).
3. `ShopifyAPI::Webhooks::Request.new` parses these headers into `shop`, `topic`, etc.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `raw_body` — it matches, so validation passes.
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: <attacker-controlled/replayed body>, ...)`, causing the host app to process attacker data attributed to `victim-shop.myshopify.com`.

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
