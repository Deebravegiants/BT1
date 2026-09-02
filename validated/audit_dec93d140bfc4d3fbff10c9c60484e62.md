### Title
Webhook shop/topic/api-version identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then dispatches the handler using the `shop`, `topic`, `webhook_id`, and `api_version` values taken directly from HTTP headers that are never included in that signature. Because a Shopify app's `api_secret_key` is a single, shared secret used to sign webhooks for every shop that installs the app (not a per-shop secret), any user who legitimately installs the app on their own store can capture a genuinely-signed `(raw_body, hmac)` pair and replay it to the app's public webhook endpoint while substituting a victim shop's domain in the `X-Shopify-Shop-Domain` header. The gem will treat the replayed payload as authentic and hand it to the merchant's webhook handler tagged with the attacker-chosen `shop`, breaking the binding between "bytes verified" and "shop acted on."

### Finding Description
`Webhooks::Registry.process` only calls `Utils::HmacValidator.validate(request)` before dispatching to the topic handler: [1](#0-0) 

`HmacValidator.validate` computes the signature exclusively from `verifiable_query.to_signable_string`, and for `Webhooks::Request` that value is only `@raw_body`: [2](#0-1) [3](#0-2) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are all pulled straight from HTTP headers with no cryptographic binding to the HMAC: [4](#0-3) 

Yet `Registry.process` passes exactly these unauthenticated fields to the handler as the acted-upon identity: [5](#0-4) 

Equality that should hold but doesn't: `shop_used_by_handler == shop_that_the_HMAC_actually_authenticates`. In reality the HMAC only authenticates `raw_body`; `shop` (and `topic`/`webhook_id`/`api_version`) are unauthenticated header bytes that ride along unchecked.

Because the `api_secret_key` used to compute this HMAC is the app's single shared secret across *all* shops that install the app (it is not shop-specific), any ordinary user can:
1. Install the target app on their own store (a completely unprivileged, self-service action requiring no stolen credentials).
2. Receive a genuine webhook at the app's public endpoint, capturing a valid `(raw_body, x-shopify-hmac-sha256)` pair signed with the app's shared secret.
3. Replay that exact `raw_body`/`hmac` pair to the same public endpoint, but with `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`) rewritten to name a *different*, victim shop that also has the app installed.

`HmacValidator.validate` will pass (the body and signature are untouched and genuinely valid), and `Registry.process` will invoke the handler with `WebhookMetadata#shop` set to the victim's domain, even though the payload never actually originated from that victim shop.

### Impact Explanation
This breaks the tenant-isolation guarantee that "an authenticated webhook body belongs to the shop header it carries." A host application built on this gem naturally trusts `WebhookMetadata#shop` (and `#topic`) as authenticated once `Registry.process` doesn't raise, since HMAC validation is documented as the authenticity check. An attacker can therefore inject attacker-controlled webhook payload content (of a topic/shape they can arrange in their own store, e.g. `orders/create`, `app/uninstalled`, `customers/data_request`, etc.) and have it processed under a different tenant's shop identity — a cross-tenant confusion that can corrupt victim-shop data, trigger unwanted business logic (e.g. spurious uninstall/GDPR cleanup, order/customer state changes) keyed on `shop`, or pollute per-shop caches/records maintained by the host app. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires no secrets, tokens, or privileged access — only the ability to install the target app on one's own (attacker-owned) shop, which is normal, self-service merchant behavior, plus basic HTTP tooling to replay a captured request with a modified header. Any publicly-installable Shopify app using this gem's webhook `Registry` is affected.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the authenticity check rather than trusting header values post-hoc:
- Include the `X-Shopify-Shop-Domain` (and other Shopify webhook headers used by the handler) in the signed/verified material, or
- Cross-check `request.shop` against a shop that is independently known to have installed the app (e.g. verify a stored session/access token exists for that shop) before dispatching, so a replayed body cannot be reattributed to an arbitrary victim domain.

### Proof of Concept
1. Install the target Shopify app on attacker-owned store `attacker-shop.myshopify.com`; trigger a webhook (e.g. `orders/create`) and capture the raw POST body `B` and header `X-Shopify-Hmac-Sha256: H` sent to the app's public webhook endpoint. `H` is `HMAC-SHA256(app_secret, B)`, valid because `app_secret` is the same secret for every shop using the app.
2. Replay the exact request to the same public endpoint, keeping body `B` and header `X-Shopify-Hmac-Sha256: H` unchanged, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (a real shop that also installed the app).
3. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(app_secret, B)` and finds it equals `H` — validation passes.
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)`, so attacker-crafted webhook content from step 1 is now processed under the victim shop's identity, even though it never came from Shopify on behalf of that shop.

### Citations

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
