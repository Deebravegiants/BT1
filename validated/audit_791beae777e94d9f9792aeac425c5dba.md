This confirms the vulnerability: `Registry.process` validates `Utils::HmacValidator.validate(request)`, which HMACs only `request.to_signable_string` (the raw body), while `request.shop` (from the `X-Shopify-Shop-Domain` header) is passed unverified into `WebhookMetadata` and given to the app's `handler.handle`.### Title
Webhook `shop` (tenant) identifier is taken from an unauthenticated HTTP header and is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body via `Utils::HmacValidator.validate(request)`. The `shop` (tenant) identity attached to that webhook, however, is read directly from the `X-Shopify-Shop-Domain` HTTP header and is never included in the HMAC-signed bytes, so it is not bound to the signature that was actually verified.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`, whose `to_signable_string` is required for HMAC verification: [1](#0-0) 

That method returns only `@raw_body`: [2](#0-1) 

Note that `hmac` (from the `X-Shopify-Hmac-Sha256` header) and `to_signable_string` (the raw body) are the only two things `HmacValidator` compares: [3](#0-2) 

But `shop` — the field that identifies *which merchant/tenant* the webhook is for — is pulled straight from the `shop-domain` header, which is completely outside the HMAC-covered byte range: [4](#0-3) 

`Registry.process` verifies the HMAC and then immediately hands the handler a `WebhookMetadata` built from `request.shop` — the unverified header value — without any secondary check that this shop matches the body's shop context: [5](#0-4) 

This is a direct structural analog to the reported `TapToken` bug: in that case, `dso_supply` accounting acted on tokens (`boostedTAP`) that were never covered by the intended "DSO-tracked emission" boundary, breaking the invariant that only DSO-sourced tokens affect `dso_supply`. Here, the equality that the HMAC is supposed to enforce is:
`HMAC_valid(raw_body, secret) == true` implies `(topic, shop, body) is authentic for that shop`.
In reality the HMAC only proves `raw_body` (i.e., the JSON payload) is authentic; it says nothing about `shop`, because `shop` is not part of `to_signable_string`. An attacker who can influence or spoof the `X-Shopify-Shop-Domain` header on a request that otherwise has a validly-signed body (e.g., a replayed/legitimate webhook body for shop A, or any body an attacker can get validly signed, combined with a header they control at the transport layer sitting in front of the app) can cause the handler to process the webhook under an arbitrary tenant identity. If the hosting application relies on `WebhookMetadata#shop` (as documented/intended, since it's the only shop identifier exposed by this struct) to select which merchant's local data/session to mutate, this breaks the tenant-isolation binding that `shop` == the merchant that owns `raw_body`.

### Impact Explanation
This falls under cross-tenant access: the gem hands application code a `shop` value that is claimed to identify the authenticated webhook source but is not actually authenticated by the one integrity check the gem performs. Any consumer of `WebhookHandler#handle` that trusts `data.shop` as the verified tenant for the given `data.body` (which is the documented purpose of this field, and the only reason it's exposed via `WebhookMetadata` after `HmacValidator.validate` passes) can be misled into applying legitimate-looking webhook data to the wrong shop's records.

### Likelihood Explanation
Exploitability depends on whether an attacker (or a misconfigured/multi-tenant reverse proxy setup) can control the `shop-domain` header independently of the signed body — this is plausible in deployments where any TLS-terminating layer forwards client-supplied headers unmodified to the app, or where Shopify's own webhook headers are otherwise not re-validated by the host framework. It requires no access token, `client_secret`, or privileged credential; the HMAC check itself still passes normally because it never touches the `shop` field in the first place.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` (or otherwise cryptographically bind them) in the value that is HMAC-verified, or independently authenticate the `shop-domain` header against the webhook body content before constructing `WebhookMetadata`. Alternatively, document in `WebhookMetadata` that `shop` is unauthenticated and must not be trusted for tenant-routing decisions without an additional binding check.

### Proof of Concept
1. A legitimate Shopify webhook for `shop-a.myshopify.com` is captured, including its valid `X-Shopify-Hmac-Sha256` value for that specific `raw_body`.
2. An attacker (or intermediary that forwards arbitrary headers to the app, e.g., a shared ingress) resends the identical `raw_body` and valid HMAC header, but rewrites `X-Shopify-Shop-Domain` to `shop-b.myshopify.com`.
3. `HmacValidator.validate(request)` in `Registry.process` succeeds because it only checks `raw_body` against the HMAC — the modified `shop-domain` header is never inspected.
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` using the attacker-controlled `shop`, and calls `handler.handle(data: ...)`.
5. If the host application uses `data.shop` to select which merchant's database row/session to update (its intended, documented use), shop-b's data is now overwritten/actioned using shop-a's payload — a cross-tenant data integrity violation.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
