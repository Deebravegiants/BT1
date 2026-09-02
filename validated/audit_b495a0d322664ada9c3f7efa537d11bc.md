### Title
Webhook HMAC only authenticates the raw body, not the `shop-domain`/`topic`/`webhook-id` headers, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authentic once `Utils::HmacValidator.validate` succeeds, but the HMAC only ever covers `Request#to_signable_string` (the raw body). The `shop`, `topic`, `webhook_id`, and `api_version` values, which are taken straight from HTTP headers, are never included in the signed content, so they are trusted without being bound to the signature that authenticates the request.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate`/`validate_signature` compute the HMAC exclusively over `verifiable_query.to_signable_string`, i.e. the raw body, using `Context.api_secret_key`: [2](#0-1) 

`Registry.process` raises `InvalidWebhookError` only if this body-only HMAC check fails, and otherwise immediately passes the *header-derived* `request.shop`, `request.topic`, and `request.webhook_id` into the handler as trusted metadata: [3](#0-2) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read directly from attacker-visible/attacker-suppliable HTTP headers (`x-shopify-shop-domain`, `x-shopify-topic`, etc.), with no cryptographic tie to the signed body: [4](#0-3) 

The equality the code implicitly assumes but never enforces is:

`shop asserted in signed bytes == shop delivered to the handler as WebhookMetadata#shop`

In reality, only the raw body is bound to the signature; `shop` (the tenant identifier) is parsed from unsigned headers. This is exactly the "field acted on but not covered by the HMAC" class: an attacker who can produce (or capture) any single valid `(raw_body, hmac)` pair — trivially available to any developer who registers a webhook for their *own*, unprivileged shop and receives one legitimate delivery from Shopify — can resend that exact body/HMAC pair to the victim app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header (and/or `x-shopify-topic`/`x-shopify-webhook-id`). `HmacValidator.validate` still succeeds because it never looked at those headers, and `Registry.process` dispatches the handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop domain.

### Impact Explanation
Any application logic in the host app that trusts `WebhookMetadata#shop` (or `#topic`/`#webhook_id`) to select which merchant's session/access token/data to act on — the officially documented pattern in `docs/usage/webhooks.md` ("construct a `Request`... call `Registry.process`... call the specified handler") — can be tricked into processing forged, attacker-controlled webhook content under a victim shop's identity, or into skipping shop-domain revalidation because the gem already claims the delivery is "verified." This crosses the tenant boundary (shop A's request treated as shop B's data) without needing the app's `client_secret`, an access token, or any privileged account — only a single legitimate delivery to the attacker's own store is required. This matches the High-impact category of a scope/expiry-style check (here, tenant-binding check) that answers permissively.

### Likelihood Explanation
Moderate. It requires the attacker to have registered at least one webhook of the target topic for a shop they control (freely available to any developer/merchant) and to be able to POST directly to the victim app's public webhook endpoint with modified headers, which is standard for any exposed HTTP webhook receiver. No secrets, tokens, or elevated privileges are required. The main variable is whether the host application actually keys sensitive behavior off `WebhookMetadata#shop`/`topic` without independently re-validating those fields against its own installation records — the gem's documentation and API design encourage exactly that reliance since `process` is presented as the authentication boundary.

### Recommendation
Include the security-relevant header values (`shop`, `topic`, `webhook_id`, `api_version`) in the signed material verified by `HmacValidator`, or otherwise cryptographically bind them to the body before dispatch (e.g., Shopify could sign a canonical string combining body + shop + topic, or the gem could require and verify the shop domain against the app's own session/installation store before invoking the handler, independent of the header value). At minimum, update `Registry.process`/`Request` so header-derived identifiers are treated as untrusted hints, and document clearly that consumers must not treat `WebhookMetadata#shop` as authenticated by `process` alone.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and registers a webhook (e.g. `orders/create`).
2. Shopify delivers a legitimate webhook to the app: body `B`, header `x-shopify-hmac-sha256: H` (valid for `B`), `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker resends the exact same `B`/`H` pair directly to the app's public webhook endpoint, replacing only `x-shopify-shop-domain: victim.myshopify.com` (and optionally forging `x-shopify-webhook-id`).
4. `Registry.process` calls `HmacValidator.validate(request)`, which recomputes HMAC over `raw_body` (`B`) only — matches `H` — and returns `true`: [5](#0-4) 
5. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed_body, ...)` believing this is an authenticated event for `victim.myshopify.com`, even though Shopify never sent any event for that shop.

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
