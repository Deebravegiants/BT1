## Title
Shopify webhook `shop` and `topic` identifiers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates the webhook HMAC only over the raw request body, while the `shop`, `topic`, `api_version`, and `webhook_id` values — read from unauthenticated HTTP headers — are handed to the application's webhook handler as if they were verified. Any attacker who can obtain one valid `(raw_body, hmac)` pair (trivially available by installing the app on their own store and receiving a real webhook) can replay that exact body/HMAC pair to the app's webhook endpoint while forging the `shopify-shop-domain` and `shopify-topic` headers to claim a different shop/topic.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from attacker-controllable headers, with no binding to the signed payload: [2](#0-1) 

`Registry.process` validates only the HMAC over the body, and then trusts `request.shop` and `request.topic` unconditionally when building `WebhookMetadata` passed to the host application's handler: [3](#0-2) 

`HmacValidator.validate` re-derives the signature purely from `to_signable_string` (i.e., the body) and the shared secret: [4](#0-3) 

The broken identity binding, stated as an equality that should hold but doesn't:
`shop_header_used_by_handler == shop_that_actually_produced_and_signed_the_body`

Before the attack: for a genuine webhook, Shopify sends `(body, hmac)` for shop A together with headers `shop-domain=A`, `topic=T`. `hmac` is valid for `body` and the app correctly treats the event as belonging to shop A.

After the attack: the attacker (who owns shop A, or otherwise obtained any one valid `(body, hmac)` pair for their own store) resends the identical `body`/`hmac` to the target app's webhook endpoint, but sets `shopify-shop-domain: B` (a victim shop) and/or `shopify-topic` to a different registered topic. `HmacValidator.validate` still returns `true`, because it only checks that `body` was signed by the app's shared secret — which it was, just for a different shop/topic than the header now claims. `Registry.process` then invokes the handler with `WebhookMetadata(shop: "B", topic: attacker_chosen_topic, body: shop_A's_body)`.

### Impact Explanation
This crosses a tenant boundary: an app built on this gem, relying on `WebhookMetadata#shop`/`#topic` as authenticated identifiers (a very natural assumption given they're delivered alongside an HMAC-validated payload), can be made to process another shop's event — or an attacker's own event masquerading as another shop's — because the gem provides no guarantee that `shop`/`topic` were part of what was actually signed. Depending on the handler logic (e.g. `app/uninstalled`, order/customer data sync, billing events), this can lead to cross-tenant data corruption, privilege changes applied to the wrong shop, or fake install/uninstall state changes attributed to a victim shop. This falls under the "cross-tenant access" Critical impact category since the gem itself is the one presenting an unauthenticated header as a trusted per-tenant identity to the caller.

### Likelihood Explanation
Any user can create a development/trial Shopify store, install the app being tested, and receive one legitimate webhook delivery, giving them a valid `(body, hmac)` pair signed with the app's own secret. Replaying that pair against the app's public webhook endpoint with forged `shopify-shop-domain`/`shopify-topic` headers requires no credentials beyond network access to the endpoint — a straightforward unprivileged-internet-user attack path, entirely enabled by this gem's `Request`/`Registry.process` implementation.

### Recommendation
Bind `shop` and `topic` (and any other header-derived, security-relevant fields) into the HMAC-signed payload verification, e.g., by including them in `to_signable_string`, or by requiring the application to independently verify that the `shop` header corresponds to a shop for which a corresponding registration/session exists before trusting `WebhookMetadata#shop`. At minimum, document prominently that `shop`/`topic` in `WebhookMetadata` are unauthenticated and must not be treated as verified tenant identifiers.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers any registered webhook topic, capturing the raw POST body and the `x-shopify-hmac-sha256` header Shopify sent.
2. Attacker POSTs to the same app's webhook endpoint using the identical body and HMAC header, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because the HMAC is still valid for the unchanged body: [5](#0-4) 
4. The registered handler receives `WebhookMetadata(shop: "victim.myshopify.com", topic: <attacker-controlled or original topic>, body: <attacker's own body>)` and performs shop-scoped actions against `victim.myshopify.com`, even though nothing from `victim.myshopify.com` was actually involved.

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
