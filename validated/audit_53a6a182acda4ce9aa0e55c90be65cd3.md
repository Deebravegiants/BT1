### Title
`Webhooks::Request#shop` is read from an unauthenticated header and is never covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the raw request body, but the `shop` (tenant) identity handed to the app's `WebhookHandler#handle` callback is taken from the `X-Shopify-Shop-Domain` HTTP header, which is not part of the signed material at all. This breaks the binding "bytes verified == bytes parsed/trusted": the HMAC verifies the body, but the app trusts the header-derived `shop` as if it were also verified.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery`, and its `to_signable_string` returns only the raw HTTP body: [1](#0-0) 

`shop` is instead pulled straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, with no cryptographic tie to the body or the HMAC: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)`, which calls `to_signable_string` (body only) and compares against the `hmac` field — it never incorporates `shop`, `topic`, or any other header into the signed payload: [3](#0-2) 

After this check passes, `Registry.process` builds a `WebhookMetadata` object directly from `request.shop` (the unauthenticated header) and hands it to the app's registered handler: [4](#0-3) 

Because the HMAC is computed only over the body, any attacker who can replay/relay a *previously observed, legitimately-signed* webhook body+HMAC pair (e.g., a webhook payload captured from their own store or leaked via logs/network capture) can freely substitute the `X-Shopify-Shop-Domain` header value to any other shop domain string. The HMAC will still validate (since it only checks the body), but the `shop` field the host application trusts as the tenant identity for that webhook event is attacker-controlled. This is exactly the analog called out in the rules: "a field acted on but not covered by the HMAC."

The `Registry` itself does not use `shop` for authorization decisions (only `topic` is used to look up the handler), but the gem passes this unauthenticated `shop` value onward to the host application's webhook handler as if it were a verified/trusted tenant identifier — there is no mechanism in this gem to detect or reject a mismatched/forged shop claim.

### Impact Explanation
This matches the High-impact category "scope or expiry check bypass" / credential-boundary confusion in the sense that the gem's own webhook-processing API silently offers an unauthenticated tenant identity (`shop`) as if it had been verified, alongside a body-only HMAC check. If a host application (following the gem's documented contract that `Registry.process` performs HMAC validation and returns a trustworthy `WebhookMetadata`) uses `data.shop` to select per-tenant secrets, sessions, or database records, cross-tenant data confusion becomes reachable purely through a network replay with a rewritten header — no access token or `api_secret_key` needed.

### Likelihood Explanation
Likelihood is limited by the precondition that the attacker must possess at least one legitimately-signed webhook body/HMAC pair (their own shop's webhook, or one intercepted in transit/logs) to replay with a different shop header, since they cannot forge a valid HMAC without the app's secret. This is a plausible scenario for a merchant/developer who receives real webhooks for their own shop and then re-sends the same body with a different `shop` header to the app's webhook endpoint, since the app cannot distinguish "legit event from Shop A" from "replayed event claiming to be from Shop B."

### Recommendation
Include the `shop` (and ideally `topic`) header values in the signed material checked by `to_signable_string`/`HmacValidator`, or, at minimum, document/enforce that `WebhookMetadata#shop` must be independently cross-checked by the host application against a known/registered shop before being trusted, since the gem's own `hmac` field never covers it. Concretely, change `Webhooks::Request#to_signable_string` (and the corresponding validation contract) so that the shop-domain header is authenticated as part of the same operation `Registry.process` relies on.

### Proof of Concept
1. App receives a legitimate webhook for `victim-shop.myshopify.com` with body `{"id":1}` and a valid `X-Shopify-Hmac-Sha256` computed by Shopify over that body.
2. Attacker (who owns/controls `attacker-shop.myshopify.com` and thus can receive their own genuinely-signed webhooks with the same body content, e.g., an empty-body test webhook `{}`) captures a valid `(body, hmac)` pair for their own shop.
3. Attacker POSTs to the app's webhook endpoint with that same valid `body`/`hmac` pair but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `@raw_body` — validation succeeds. `Registry.process` then constructs `WebhookMetadata.new(... shop: request.shop ...)` using the forged header value and invokes the app's handler, which now believes the event pertains to `victim-shop.myshopify.com`. [4](#0-3)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
