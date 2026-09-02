### Title
Webhook HMAC only signs the raw body, letting a captured (body, hmac) pair be replayed with a spoofed shop/topic identity - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, and `Utils::HmacValidator.validate` checks the HMAC exclusively against that body. The `shop-domain` and `topic` headers that `ShopifyAPI::Webhooks::Registry.process` uses to route and identify the payload are never included in the signed bytes, so the identity binding `hmac(secret, raw_body) == received_hmac` is disconnected from the binding `shop-domain header == shop the payload actually belongs to`.

### Finding Description
`Request#hmac` and `Request#to_signable_string` expose only the decoded `X-Shopify-Hmac-Sha256`/body pair to the validator: [1](#0-0) 

`Utils::HmacValidator.validate` recomputes `HMAC(secret, to_signable_string)` and compares it to the supplied signature — it never touches `shop`, `topic`, `webhook_id`, or `api_version`: [2](#0-1) 

`Registry.process` trusts `request.topic` for handler dispatch and `request.shop` for the identity passed into the handler, based solely on the outcome of that body-only HMAC check: [3](#0-2) 

Because the `shopify-shop-domain` and `shopify-topic` headers are plain, unauthenticated HTTP headers with respect to the signature, any unprivileged user who can obtain one legitimately-signed `(raw_body, hmac)` pair — for example by installing the app on their own store and letting Shopify deliver a real webhook to them — can replay that exact body and HMAC to the app's webhook endpoint while substituting a different `shopify-shop-domain` (or `shopify-topic`) header value. `HmacValidator.validate` still returns `true`, because it only re-derives the HMAC over `@raw_body`, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload came from the attacker-chosen shop and/or route it to a different topic handler than Shopify actually signed for.

This is the same class of defect as the source report: a value that is acted upon (`isDepositAllowed`/here, `shop`/`topic` identity) is not covered by the same guard that is assumed to authenticate the whole message (`isDepositAllowed` check/here, HMAC over the full signable content).

### Impact Explanation
An attacker with no privileges beyond running their own store on the same app can forge the `shop`/`topic` identity of an otherwise validly-HMAC'd webhook delivery. Any host application that relies on `WebhookMetadata#shop` (as returned by this gem, per `docs/usage/webhooks.md` and `lib/shopify_api/webhooks/webhook_handler.rb`) to determine which tenant's data/session to act on is exposed to cross-tenant confusion: data belonging to shop A can be replayed and attributed to shop B, or a body meant for a benign topic can be redelivered under a security-sensitive topic (e.g. `shop/redact`, `customers/redact`) that a handler trusts implicitly because "the HMAC was valid." This crosses the tenant/authentication boundary defined by the gem's own webhook-verification contract, qualifying as Critical (cross-tenant access) under the program's rubric.

### Likelihood Explanation
Likelihood is moderate-to-high: obtaining one legitimate `(raw_body, hmac)` pair requires nothing more than being any customer/merchant who can trigger a webhook-eligible event on a store that has this app installed (installing a dev/trial app is unprivileged and does not require `api_secret_key` or any leaked credential). Replaying it with modified headers only requires sending a normal HTTP POST to the app's public webhook endpoint.

### Recommendation
Bind the identity fields into the signed content that `HmacValidator` verifies, e.g. include `shop`, `topic`, and `webhook_id` in `Request#to_signable_string` (or verify them out-of-band against a value the app already trusts, such as the session/shop the webhook was registered for) so that a valid HMAC can only be produced for the exact `(body, shop, topic)` tuple Shopify actually signed, not for any header combination an attacker chooses to attach to a previously captured body.

### Proof of Concept
1. App developer installs their own app on `attacker-shop.myshopify.com` and registers a webhook handler for topic `orders/create` via `ShopifyAPI::Webhooks::Registry`.
2. Shopify delivers a legitimate webhook to the app's endpoint:
   - Headers: `X-Shopify-Topic: orders/create`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`
   - Body: `{"id": 1, ...}`
3. Attacker captures this exact `(raw_body, hmac)` pair (trivial, since it's their own store's traffic hitting their own reachable endpoint, or any endpoint they can observe).
4. Attacker crafts a new POST to the same webhook endpoint reusing the identical `raw_body` and `X-Shopify-Hmac-Sha256` value, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (or changes `X-Shopify-Topic` to `customers/redact`).
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, raw_body)` — matching, since the body is unchanged — and proceeds to call the handler with `WebhookMetadata.new(topic: "customers/redact"/attacker-chosen, shop: "victim-shop.myshopify.com", body: parsed_body, ...)`, despite Shopify never having signed a payload for that shop/topic combination. [4](#0-3)

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
