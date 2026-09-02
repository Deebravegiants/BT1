### Title
Cross-tenant webhook spoofing via unauthenticated `shop-domain`/`topic` headers not bound to the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` (and `topic`) values from raw HTTP headers, while `Utils::HmacValidator` only verifies the HMAC over `to_signable_string`, which for a webhook `Request` is defined as `@raw_body` alone. The `shop` value that a handler uses to attribute the event to a tenant is never covered by the signature that `Registry.process` checks, breaking the intended equality `shop authenticated by HMAC == shop the webhook data is processed for`.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` is the sole authenticity gate for inbound webhooks: [1](#0-0) 

It calls `Utils::HmacValidator.validate(request)`, which computes `HMAC(secret, request.to_signable_string)` and compares it to `request.hmac`: [2](#0-1) 

But `Request#to_signable_string` returns only the raw body, and `Request#shop`/`Request#topic` are read straight from attacker-influenceable HTTP headers, completely outside the signed content: [3](#0-2) 

Because the app's `api_secret_key` is a single, static, app-wide secret (not per-shop), any tenant that installs the app can legitimately trigger a webhook and thus obtain a valid `(raw_body, hmac)` pair signed with that same shared secret. Nothing in `Request` or `HmacValidator` binds that valid signature to the `shop-domain` header value. An attacker who has captured or triggered one authentic `(body, hmac)` pair from their own store can re-send an HTTP request directly to the app's public webhook endpoint with the identical body/HMAC but a forged `x-shopify-shop-domain` header naming a victim shop (and/or a different `x-shopify-topic`). `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` passes the forged `shop` straight to the handler: [4](#0-3) 

The documented usage pattern confirms host apps are expected to trust `data.shop` for tenant identification without any additional gem-level check: [5](#0-4) 

This is the "field acted on but not covered by the HMAC" class of bug: the identity-binding equality `HMAC-authenticated bytes == bytes that determine the tenant (shop)` does not hold, because `shop` is parsed from an unauthenticated header while only the body is authenticated.

### Impact Explanation
A successful forgery lets any app-installing tenant (an unprivileged, low-barrier "unpriviledged internet user" in the sense that installing a dev/trial store requires no special access) inject attacker-controlled webhook payloads that the app processes as belonging to a different, victim shop. Depending on the host app's webhook handler logic (e.g., updating orders/products/customers data keyed by `data.shop`), this can result in cross-tenant data corruption or cross-tenant state changes attributed to the victim's shop — a boundary violation between tenants that the HMAC check is nominally supposed to prevent.

### Likelihood Explanation
Exploitation requires the attacker to already be able to trigger at least one legitimately signed webhook (trivial — install the app on any store, including a free development store) and to be able to send arbitrary HTTP requests directly to the app's public webhook endpoint (also trivial, since that endpoint must be internet-reachable for Shopify to call it). No access to `api_secret_key`, tokens, or TLS interception is required. The only defenses would be host-app-specific additional checks not provided or documented by this gem.

### Recommendation
Bind the shop (and ideally topic) into the HMAC-covered signable content, or otherwise cryptographically tie the header-derived `shop`/`topic` values to the signature, e.g., include them in `to_signable_string` for `Webhooks::Request`, or expose a method that lets `Registry.process` cross-check that the `shop`/`topic` reported by headers are consistent with values embedded in the signed body (Shopify webhook payloads typically include the shop's `myshopify_domain` in the JSON body, which could be compared against the header value before dispatching to the handler).

### Proof of Concept
1. Install the target app on attacker-controlled store `attacker.myshopify.com`; trigger any subscribed webhook topic to receive a legitimate request with body `B` and header `x-shopify-hmac-sha256: H = HMAC(secret, B)`.
2. Craft a new POST request to the app's public webhook endpoint with the same raw body `B` and same `x-shopify-hmac-sha256: H`, but set `x-shopify-shop-domain: victim.myshopify.com` (and/or change `x-shopify-topic`).
3. `ShopifyAPI::Webhooks::Registry.process` computes the HMAC solely over `B`, which matches `H`, so `Utils::HmacValidator.validate` returns `true`.
4. The handler is invoked with `WebhookMetadata` whose `shop` is `"victim.myshopify.com"`, even though the payload actually originated from and was signed for `attacker.myshopify.com`, achieving cross-tenant attribution of attacker-controlled webhook data.

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

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** docs/usage/webhooks.md (L10-17)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
