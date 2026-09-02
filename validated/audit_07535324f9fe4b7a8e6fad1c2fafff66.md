## #Vulnerability found

### Title
Webhook `shop` and `topic` fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers. `Registry.process` validates the HMAC and then dispatches the handler using those unauthenticated header values, breaking the binding between "bytes verified" and "identity acted upon" — the same class of bug as the reported issue (`MessageType` acted upon but not covered by the signed encoding).

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, `#api_version` are all read from HTTP headers, which are never part of the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC (`Utils::HmacValidator.validate(request)`), and if it passes, looks up the handler by `request.topic` and dispatches `WebhookMetadata` carrying `request.shop`, `request.topic`, etc. — all values that were never covered by the signature: [3](#0-2) 

`HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` using `Context.api_secret_key` — the **same secret for every shop** that has installed the app: [4](#0-3) 

The broken identity binding, stated as an equality that the code assumes but does not enforce:
`shop/topic used to route+process the webhook == shop/topic that was actually authenticated by the HMAC`

In reality, the HMAC only proves: `raw_body was signed with Context.api_secret_key`. It says nothing about which shop or topic that body was meant for. Because the same `api_secret_key` is shared across all shops using the app, any attacker who has one legitimate app installation (e.g., a free/dev store) can capture a valid `(raw_body, hmac)` pair from their own store's webhook delivery, then replay it against the app's webhook endpoint with the `shopify-shop-domain` header changed to a victim shop, and/or the `shopify-topic` header changed to a different registered topic. `HmacValidator.validate` will still return `true` because the body and HMAC are unchanged and still match the shared secret, but `Registry.process` will dispatch the attacker-controlled body to the handler under the victim's shop identity and/or a different topic's handler than the one Shopify actually sent it for.

### Impact Explanation
This is a cross-tenant identity-confusion vulnerability (High/Critical depending on app logic): a handler written under the reasonable assumption that "this webhook body legitimately came from `data.shop` for `data.topic`" (as documented in `docs/usage/webhooks.md` and exercised in `WebhookMetadata`) can be tricked into processing attacker-supplied bytes as if they originated from a different shop or under a different topic, since `Registry.process` trusts `request.shop`/`request.topic` immediately after HMAC validation passes: [5](#0-4) 
Depending on how the consuming app uses `WebhookMetadata#shop` (e.g., to look up the merchant record and apply the body's data), this can lead to cross-tenant data corruption/exfiltration or to a topic-confusion attack (e.g., feeding `orders/create` shaped JSON into a `customers/redact` handler or vice versa) purely by controlling headers of a replayed, still-validly-signed request.

### Likelihood Explanation
Any developer/attacker who is a legitimate merchant of the app (a very low bar — install the app on a free dev store) can obtain one valid `(raw_body, hmac)` pair for any topic they want by simply triggering that event in their own store, then replay it to the app's public webhook endpoint with modified `shopify-shop-domain`/`shopify-topic` headers. No access to `api_secret_key`, tokens, or privileged accounts is required — this is exploitable by any unprivileged internet user who can install the target app once.

### Recommendation
Bind `shop-domain` and `topic` (and ideally `webhook-id`/`api-version`) into the HMAC-signed payload used for verification (e.g., include them, along with the raw body, in `to_signable_string`), or independently verify that the `shop-domain` header corresponds to a shop actually known/installed by the app before dispatching. At minimum, document that `Registry.process` does not authenticate `shop`/`topic` and instruct consuming apps to cross-check them against their own install records.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store (`attacker-shop.myshopify.com`) and registers/triggers a webhook (e.g., `orders/create`) to receive a legitimate `(raw_body, shopify-hmac-sha256)` pair.
2. Attacker sends a POST to the app's webhook endpoint with the exact same `raw_body` and `shopify-hmac-sha256` header, but with `shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `shopify-topic`).
3. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers (headers aren't validated against the body).
4. `Utils::HmacValidator.validate(request)` recomputes HMAC over `raw_body` with `Context.api_secret_key` — identical to step 1 — and returns `true`.
5. `Registry.process` dispatches the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: <attacker's raw_body>, ...)`, causing the app to process attacker-controlled data attributed to the victim shop.

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
