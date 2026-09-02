Found it: `ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from an unauthenticated header, while the HMAC only covers the request body.

### Title
Webhook `shop-domain` Header Is Trusted Without Being Covered by the HMAC, Allowing Cross-Tenant Handler Invocation - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook request by computing an HMAC over the raw request body only, then trusts the `shop-domain`/`x-shopify-shop-domain` header verbatim to populate `WebhookMetadata#shop`, which is handed to the app's webhook handler as the tenant identifier.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . The `shop` accessor is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, independent of that signature: [2](#0-1) .

`Registry.process` validates the HMAC (over the body) and then immediately forwards `request.shop` (the unauthenticated header value) into `WebhookMetadata` passed to the handler: [3](#0-2) .

`Utils::HmacValidator.validate` computes the signature only from `to_signable_string` of the given `VerifiableQuery`: [4](#0-3) . For `Webhooks::Request`, that signable string is the raw body only — it never includes `shop`, `topic`, `api_version`, or `webhook_id`. This breaks the equality that should hold: `bytes verified by HMAC == bytes the shop identity is derived from`. An attacker who can produce *any* request with a body whose HMAC is valid for the app's secret (e.g., replaying/relaying a legitimate webhook delivery for one shop, or a payload that happens to validate for a re-used/shared body across shops in a multi-tenant proxy/gateway sitting in front of the app) can supply an arbitrary `shop-domain` header value, since that header is never part of what is cryptographically checked.

This matches the report's bug class: Apache's flaw was trusting a path element that was verified separately from the one actually used to resolve the resource (verified alias vs. actually-accessed file). Here, the byte range that is HMAC-verified (body) differs from the byte range used to establish tenant identity (the `shop-domain` header), i.e. "bytes verified versus bytes parsed."

### Impact Explanation
If a host application's webhook handler uses `data.shop` (the value straight from `WebhookMetadata`) to look up per-shop state, credentials, or to route write operations without independently confirming the shop against its own authoritative HMAC-covered channel, an attacker able to control or replay the `shop-domain` header of an otherwise-HMAC-valid request can cause the handler to act on behalf of the wrong tenant — a cross-tenant data/action confusion. This is exploitable purely at the network layer sitting between Shopify and the app (e.g., a proxy, load balancer, or any intermediary that lets headers be modified/replayed while the raw body — and thus the HMAC — remains unchanged), and requires no `api_secret_key`, access token, or other credential from the attacker.

### Likelihood Explanation
Exploitability depends on whether an attacker can influence the `shop-domain` header independently of the body for a request the app will treat as a validly signed webhook. Because many deployments terminate TLS and route based on headers at infrastructure the app operator doesn't fully control, and because the HTTP header is explicitly separate from the signed payload, this is a realistic exposure surface even though it requires a delivery path where headers and body can be manipulated independently while body-derived HMAC still validates (e.g., a captured/replayed valid webhook delivery with the shop header altered downstream, or any component between the internet and the app that can rewrite headers without access to the body's meaning).

### Recommendation
Include `shop`, `topic`, `api_version`, and `webhook_id` in the value that is HMAC-verified (or otherwise cryptographically bind them to the body), so the shop identity used in `WebhookMetadata` is guaranteed to be the same one Shopify actually signed for. At minimum, document/enforce that the `shop-domain` header must not be trusted for tenant-sensitive lookups unless it is separately corroborated (e.g., against `Context` known-shop state or another authenticated channel).

### Proof of Concept
1. Capture (or otherwise obtain) a validly-signed webhook request for `shop-a.myshopify.com` with a given `{}` (or any) body — the HMAC in `x-shopify-hmac-sha256` is valid because it is computed only from the raw body, per `HmacValidator.validate_signature`: [5](#0-4) .
2. At any intermediary capable of rewriting headers without recomputing the signature (which is only over the body), change `x-shopify-shop-domain` to `shop-b.myshopify.com` and forward the same body/HMAC.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the (unchanged) body against the (unchanged) HMAC: [6](#0-5) .
4. The handler receives `WebhookMetadata` with `shop: "shop-b.myshopify.com"` even though the signed payload was never bound to that shop: [7](#0-6) , causing the app to perform shop-b's webhook processing logic using data that was only ever signed as "some payload," not as "shop-b's payload."

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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
