### Title
Webhook `shop-domain` and `topic` headers are trusted for routing/attribution without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook's authenticity solely by checking the HMAC over the raw request body. The `shop-domain` and `topic` values, which are read from unauthenticated HTTP headers and then used both to select the handler and to identify which tenant/shop the payload belongs to, are never included in the signed material. This breaks the intended identity binding `HMAC == f(shop, topic, body)` and instead only enforces `HMAC == f(body)`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` and `topic`, however, come from caller-supplied HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` computes and compares the signature over exactly that signable string (the body only): [3](#0-2) 

`Registry.process` then uses the *unverified* `request.topic` to select the handler and passes the *unverified* `request.shop` straight into the metadata handed to the app's business logic: [4](#0-3) 

Because only the body bytes are authenticated, any two values of `shop`/`topic` paired with the *same* body produce an *identical, still-valid* HMAC. An attacker who can obtain one legitimate `(body, hmac)` pair from Shopify — trivially done by installing the target app on a shop the attacker owns and controls, and capturing any webhook delivery Shopify sends for that install — can replay that exact `raw_body` + `x-shopify-hmac-sha256` value to the app's webhook endpoint while forging the `x-shopify-shop-domain` header to name a victim shop and/or forging `x-shopify-topic` to route to a different handler. The signature check in `HmacValidator.validate` still passes because it never inspects those headers, so `Registry.process` will invoke the handler and hand it `WebhookMetadata` claiming the payload originated from — and should be attributed to — the victim shop.

This is the exact bug class described in the analog report: a field that the application acts on (`shop`, `topic`) is not covered by the integrity check (`HMAC` over body only), so the "verified" side and the "acted upon" side of the equality diverge.

### Impact Explanation
Host applications built on this gem commonly use `WebhookMetadata#shop` to look up the corresponding shop/session record and then act on that shop's data (e.g., `Shop.find_by(shopify_domain: data.shop)` followed by writes, deletions, or triggering of shop-scoped side effects using that shop's stored access token). Because `shop` is not authenticated, an attacker controlling only their own shop's legitimate webhook traffic can cause the receiving application to process attacker-controlled webhook bodies under the identity of an arbitrary victim shop, and/or force dispatch to a handler for a topic that was never actually delivered for that body (e.g., replaying an `orders/create` payload while spoofing the `customers/redact` topic header). This is a cross-tenant identity-binding break reachable by any unprivileged internet user who owns a development/test shop capable of installing the target app.

### Likelihood Explanation
Likelihood is high for any app that (a) uses the gem's webhook `Request`/`Registry.process` flow as documented, and (b) derives shop or topic identity from `WebhookMetadata` rather than independently re-deriving it from signed content. Obtaining a valid `(body, hmac)` pair requires nothing more than installing the target app on a shop the attacker controls — a normal, unprivileged action — and capturing one webhook delivery.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the signable string used for HMAC verification (or otherwise cryptographically bind them, e.g. by deriving the shop from a separately validated source such as an authenticated session/API call rather than trusting the header), so that `Utils::HmacValidator.validate` cannot succeed unless the exact `(shop, topic, body)` tuple that Shopify actually signed is presented.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a shop they legitimately own/control).
2. Shopify delivers a real webhook, e.g. `orders/create`, to the app's endpoint with headers:
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-topic: orders/create`
   - `x-shopify-hmac-sha256: <valid HMAC of raw_body>`
3. Attacker captures `raw_body` and `x-shopify-hmac-sha256` from step 2.
4. Attacker sends a new HTTP request to the same webhook endpoint with the identical `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds a `Request` whose `hmac` matches (`to_signable_string` only ever returns `raw_body`), so `Utils::HmacValidator.validate(request)` in `Registry.process` returns `true`.
6. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: <attacker's payload>, ...)`, causing the host application to process attacker-controlled data under the victim shop's identity.

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
