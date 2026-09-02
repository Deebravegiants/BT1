### Title
Webhook `shop`/`topic`/`webhook_id`/`api_version` identifiers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw body via `to_signable_string`, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers and never bound into the HMAC-verified bytes. `Registry.process` trusts these unauthenticated header values to route the payload to a handler and to populate `WebhookMetadata#shop`, breaking the identity binding `bytes verified == bytes acted on`.

### Finding Description
`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` and compares it against the `hmac` accessor [1](#0-0) . For webhook requests, `to_signable_string` returns only `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are parsed exclusively from HTTP headers that are entirely outside the signed content [2](#0-1) .

`Registry.process` validates only that the HMAC matches the body, then dispatches based on the unauthenticated `request.topic` and constructs `WebhookMetadata` using the unauthenticated `request.shop`, `request.webhook_id`, and `request.api_version`: [3](#0-2) 

Because the app's `client_secret` is shared across every shop that installs the app, any unprivileged merchant can legitimately install the app on their own store and receive a genuinely-signed webhook (e.g. `app/uninstalled` with an empty `{}` body, or any payload whose shape the attacker controls or can predict). The pair `(raw_body, hmac)` from that legitimate webhook remains valid for *any* combination of `shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, and `shopify-api-version` headers, because none of those fields are part of the signed input. An attacker can therefore replay that captured `(body, hmac)` pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header of a victim shop (and/or a different topic), and `HmacValidator.validate` will still return `true` since only the body bytes are checked [4](#0-3) .

The equality that should hold is:
`bytes cryptographically verified (raw_body only)` == `bytes the application acts on to determine tenant/topic identity (shop, topic, webhook_id, api_version headers)`

This equality does not hold: the verified set is a strict subset of the acted-upon set, so `shop`/`topic`/`webhook_id`/`api_version` are effectively unauthenticated and attacker-controlled once any single valid `(body, hmac)` pair is obtained.

### Impact Explanation
This is a cross-tenant identity confusion: an app built on this gem cannot distinguish, from `Registry.process`, whether a webhook that carries a validly-signed body truly originated for the shop named in the `shop` header. A host application that uses `WebhookMetadata#shop` to select the tenant record/data to mutate (a documented and expected usage pattern shown in the gem's own webhook docs) can be tricked into applying an attacker's forged/replayed body under a victim shop's identity, or into misrouting mandatory compliance topics (`shop/redact`, `customers/redact`, `customers/data_request`) to the wrong handler/shop context. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any account that can install the app on a shop it controls (a fully unprivileged, self-service action for any Shopify merchant) can obtain a validly HMAC-signed `(body, hmac)` pair without ever seeing `api_secret_key`. From there, forging the `shopify-shop-domain`/`shopify-topic`/`shopify-webhook-id`/`shopify-api-version` headers requires no cryptographic material at all — the endpoint is a public HTTP webhook receiver by design. Likelihood is high wherever the host app keys any authorization or data-selection logic on `WebhookMetadata#shop`/`#topic` without independently re-validating shop ownership (e.g., cross-checking against a known-registered shop/session store).

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the signable content used for HMAC verification (or otherwise cryptographically bind them, e.g. by validating the `shop` header against a shop-scoped webhook secret / registered session rather than trusting it verbatim). At minimum, document prominently that `WebhookMetadata#shop`/`#topic` are unauthenticated header values and that host applications must independently verify the shop is one the app has an active install/session for before acting on webhook data.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers a webhook whose body is `{}` (e.g. `app/uninstalled`), receiving a request with headers:
   - `X-Shopify-Hmac-Sha256: <valid HMAC of "{}">`
   - `X-Shopify-Shop-Domain: attacker.myshopify.com`
   - `X-Shopify-Topic: app/uninstalled`
2. Attacker replays the exact same raw body (`{}`) and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but rewrites `X-Shopify-Shop-Domain` to `victim.myshopify.com` and/or `X-Shopify-Topic` to `shop/redact`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `@raw_body` ("{}") [5](#0-4)  — validation succeeds despite the forged shop/topic.
4. The handler registered for the forged topic is invoked with `WebhookMetadata.new(topic: "shop/redact", shop: "victim.myshopify.com", ...)` [6](#0-5) , causing the host application to act as though a genuine, verified webhook arrived from `victim.myshopify.com`.

### Citations

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
