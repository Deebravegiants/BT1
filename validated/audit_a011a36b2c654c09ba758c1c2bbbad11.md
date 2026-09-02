I have enough evidence to write up the finding.

### Title
Webhook HMAC signs only the raw body, not the `shop-domain`/`topic`/`webhook-id` headers, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signature over the raw request body alone, while the `shop` (and `topic`/`webhook_id`) fields — which are trusted and acted upon by `ShopifyAPI::Webhooks::Registry.process` — come from unauthenticated HTTP headers that are not covered by that signature. This breaks the intended binding `hmac == HMAC(secret, shop || topic || body)` down to `hmac == HMAC(secret, body)`, letting an attacker present a genuinely-signed body under an arbitrary `shop` identity.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `hmac` is derived purely from the `hmac-sha256` header: [2](#0-1) 

Meanwhile `shop`, `topic`, and `webhook_id` are pulled straight from headers with no cryptographic binding to the signed payload: [3](#0-2) 

`Registry.process` validates only that HMAC-over-body check, then immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`) to build the data handed to the app's `WebhookHandler`: [4](#0-3) 

`Utils::HmacValidator.validate` only ever checks `verifiable_query.hmac` against `verifiable_query.to_signable_string`, i.e. the raw body in this case — it never incorporates the headers: [5](#0-4) 

The `WebhookMetadata` struct passed to the host application's handler carries this unauthenticated `shop` value directly: [6](#0-5) 

Because every shop that installs the app shares the same app-level `client_secret` (`api_secret_key`) for computing webhook HMACs, an attacker who controls (or has installed the app on) any single Shopify store can legitimately receive real webhooks with a correctly-computed HMAC for a given `raw_body`. Since the signature never covers `shop-domain`, that same `(raw_body, hmac)` pair remains valid when replayed to the app's webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop. `Registry.process` will pass HMAC validation (it only checks the body) and dispatch to the handler with `shop: <victim-shop>`, `body: <attacker-controlled/replayed body>`.

This is the same bug class as the referenced report: a field that is acted upon (`shop`, which determines tenant identity) is not covered by the authentication primitive (`hmac`) that is supposed to bind the whole message — exactly the "field acted on but not covered by the HMAC" pattern.

### Impact Explanation
Any host application that uses `WebhookMetadata#shop` to look up/attribute data (e.g., to find the merchant's session/access token, or to write incoming webhook payloads into per-tenant storage) can be made to associate attacker-supplied, replayed webhook data with an arbitrary victim shop identifier. This is a cross-tenant boundary violation: the gem's own webhook verification primitive does not bind the claimed tenant (`shop`) to the cryptographic proof, so the host app cannot rely on `HmacValidator.validate` + `request.shop` together as a safe per-tenant authentication check, even though the gem's public API implies exactly that pairing is safe (`Registry.process` does the "HMAC-then-trust-shop" flow internally).

### Likelihood Explanation
Requires no privileged credentials: an attacker only needs the ability to trigger any real webhook delivery under an account they control (e.g., install the app on their own free/dev store), which is available to any unprivileged internet user. Replaying the captured `raw_body`/`hmac-sha256` pair with a modified `shop-domain` header is trivial once obtained.

### Recommendation
Include the trusted identity fields (at minimum `shop`, and ideally `topic`/`webhook-id`) in the value that is authenticated, or otherwise require verification that the `shop-domain` header corresponds to a session/shop the caller is authorized to act as, rather than relying on Shopify's own signature (which is only ever computed over the body) as a stand-in for tenant authentication. At a minimum, document clearly in `Registry.process`/`Request` that `request.shop` is unauthenticated and must not be trusted for tenant attribution without an independent binding (e.g., matching against the URL path a store's webhooks are delivered to, or comparing against a known list of shops previously installed), since `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb`) never signs it.

### Proof of Concept
1. Attacker installs the target app on their own Shopify dev store `attacker.myshopify.com`.
2. Shopify sends a legitimate webhook (e.g. `orders/create`) to the app's endpoint with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of body B>`, and raw body `B`.
3. Attacker captures `B` and the valid HMAC value.
4. Attacker replays a request to the same endpoint with identical body `B` and identical `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `body` against `hmac` — see `lib/shopify_api/utils/hmac_validator.rb:12-22` and `lib/shopify_api/webhooks/request.rb:35-38`.
6. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed(B), ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the host application to process attacker-controlled data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
