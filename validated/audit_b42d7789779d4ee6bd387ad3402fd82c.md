## Title
Webhook shop/topic identity fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook by validating an HMAC that covers **only the raw request body**, then dispatches the request and hands the handler a `shop`, `topic`, `webhook_id`, and `api_version` that are all read straight from **unauthenticated HTTP headers**. The equality the library implicitly relies on — "the tenant/topic that the verified HMAC bytes belong to" == "the tenant/topic handed to the webhook handler" — is never actually checked, because those identity fields are not part of the signed payload.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

All the other request attributes used later to route and label the webhook — `topic`, `shop`, `api_version`, `webhook_id` — are pulled directly from HTTP headers with no cryptographic binding to the body: [2](#0-1) 

`Utils::HmacValidator.validate` computes and compares the signature strictly against `verifiable_query.to_signable_string`, i.e. the body only: [3](#0-2) 

`Registry.process` uses this single body-only HMAC check as the sole authentication gate, then trusts the header-derived `shop`/`topic`/`webhook_id`/`api_version` to select the handler and populate the metadata passed to application code: [4](#0-3) 

Because the app-wide `api_secret_key` (not a per-shop secret) is used to compute the HMAC, any tenant that has legitimately installed the app can obtain a validly-signed `(body, hmac)` pair from a real Shopify-delivered webhook for their own shop, then replay that exact body+HMAC to the app's public webhook endpoint while substituting the `x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`, or `x-shopify-api-version` headers. `HmacValidator.validate` still succeeds (it never inspects headers), `Registry.process` still routes to whatever handler the attacker names via the `topic` header, and the handler receives a `WebhookMetadata` object whose `shop` claims to be a different, victim tenant while `body` is fully attacker-influenced (an idle low-privilege tenant can generate arbitrary webhook bodies for topics they subscribe to, e.g. `customers/update`, `orders/create`). This exactly mirrors the analog class called out: *"a field acted on but not covered by the HMAC"* — the ERC721-style bug is "checked presence/success but not the exact bound value"; here the gem checks "an HMAC is valid" but never checks that the HMAC's signer is actually bound to the `shop`/`topic` that the code proceeds to trust.

### Impact Explanation
This is a cross-tenant identity-binding break: an app built on this gem that persists/looks-up per-shop state keyed by `WebhookMetadata#shop` (session lookup, data updates, redaction requests, etc., which is the documented usage pattern per `docs/usage/webhooks.md`) can be made to apply attacker-controlled webhook `body` data under a victim shop's identity, since `shop` is never authenticated against the payload that was actually HMAC-verified. This matches the "cross-tenant access" Critical impact category — data or actions from one tenant can be attributed to and executed against another tenant's context purely because the gem-provided verification primitive omits `shop`/`topic` from the signed material.

### Likelihood Explanation
Exploitation only requires having *any* shop where the app is installed (any developer/merchant can install a public app on a store they control) — no access to `api_secret_key`, no privileged account, and no TLS interception is needed. The attacker simply captures one legitimately delivered webhook for their own shop and re-POSTs it to the app's public webhook endpoint with edited headers; the gem's `Registry.process`/`HmacValidator.validate` path does not detect this because the signed bytes (the body) are literally unmodified.

### Recommendation
Bind the tenant/topic identity into the material that is HMAC-verified, or otherwise cryptographically/authoritatively tie the header-derived `shop` to the verified payload before it is handed to application handlers, e.g.:
- Include `shop`, `topic`, and `webhook_id` in `to_signable_string` (or otherwise validate them against a Shopify-issued, independently-authenticated source such as an existing offline session for that shop) rather than trusting the values purely from headers.
- At minimum, document/enforce in `Registry.process` that `request.shop` must correspond to a shop with a currently valid, previously established session before the handler is invoked, so a replayed webhook for shop A cannot be trivially relabeled as shop B.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; subscribe to `customers/update` webhooks.
2. Trigger the webhook legitimately; capture the raw POST body and the `x-shopify-hmac-sha256` header Shopify computed with the app's `api_secret_key`.
3. Replay the identical body + HMAC header to the app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) calls `Utils::HmacValidator.validate(request)` which passes because it only checks the (unmodified) body against the (unmodified) HMAC — see `lib/shopify_api/utils/hmac_validator.rb:12-31` and `lib/shopify_api/webhooks/request.rb:35-38`.
5. The registered handler for `customers/update` receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and attacker-chosen `body`, despite the HMAC never having verified anything about `victim.myshopify.com`.

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
