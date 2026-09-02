## Finding

`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw HTTP body — it never includes the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers in the bytes that get HMAC-verified: [1](#0-0) 

Yet `Registry.process` trusts those same unauthenticated headers to route and identify the webhook after HMAC validation passes: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.to_signable_string` against the HMAC, i.e. body bytes only: [3](#0-2) 

### Title
Webhook `shop-domain`/`topic`/`webhook-id` headers are not covered by the HMAC, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `Utils::HmacValidator.validate` verifies nothing about the `x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`, or `x-shopify-api-version` headers. `Registry.process` nevertheless trusts these unauthenticated headers to select the handler (`@registry[request.topic]`) and to populate `WebhookMetadata` (`shop:`, `webhook_id:`, `api_version:`) passed to the host app's handler.

### Finding Description
The identity binding that should hold is: `bytes verified by HMAC == bytes the app acts on for shop/topic identity`. Here it does not — the HMAC only proves the body was signed with the app's `api_secret_key` at some point; it says nothing about which shop, topic, or webhook ID that body is currently being delivered under.

Critically, `api_secret_key` is the app's single, shared secret — it is not scoped per shop/tenant (see `HmacValidator.validate` at [4](#0-3) ). Any shop that installs the app can legitimately trigger webhook deliveries to the app's endpoint (e.g. by creating an order), each with a body correctly HMAC-signed by Shopify using that same shared secret. An attacker who owns/controls one such shop (an "unprivileged internet user" relative to other tenants of the same app) can capture one of these legitimately-signed `(raw_body, hmac)` pairs, then replay that exact HTTP body and HMAC header to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header (and/or `x-shopify-topic`, `x-shopify-webhook-id`) to point at a victim shop that also uses the app.

`HmacValidator.validate` passes because the body+HMAC pair is genuinely valid for that secret. `Registry.process` then dispatches based on the spoofed `topic` header and hands the handler a `WebhookMetadata` claiming the spoofed `shop`, letting attacker-controlled body content be processed as though it originated from — and pertains to — a different tenant.

### Impact Explanation
This crosses a tenant boundary: an attacker-controlled webhook body can be attributed to another merchant's shop domain, or delivered under an attacker-chosen topic (e.g. spoofing `app/uninstalled`, `customers/redact`, or other mandatory/compliance topics) purely by changing headers that are not part of the signed material. Depending on how the host application's webhook handlers use `shop`/`topic` (which most apps do, to look up/mutate per-tenant records), this enables cross-tenant data corruption or unauthorized actions attributed to another merchant — matching the "cross-tenant access" Critical impact class.

### Likelihood Explanation
Exploitation requires the attacker to be an actual installer of the target app (to legitimately trigger a signed webhook body under the shared `api_secret_key`) and requires the host app's handler logic to trust `shop`/`topic`/`webhook_id` from `WebhookMetadata` for tenant-scoped decisions — which is exactly how the gem's documented API expects developers to use it (`data.shop`, `data.topic` are the only shop/topic identifiers exposed). No access to any credential beyond ordinary app installation is required.

### Recommendation
Include the identifying headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable string used for HMAC verification, or otherwise cryptographically bind them to the verified body, so header spoofing cannot decouple the verified bytes from the metadata the app acts on.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com`.
2. Attacker triggers a real event (e.g. creates an order) causing Shopify to deliver a webhook to the app's endpoint with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
3. Attacker intercepts/replays this request to the same endpoint, keeping body `B` and header `H` unchanged, but sets `x-shopify-shop-domain: victim.myshopify.com` (and optionally spoofs `x-shopify-topic`).
4. `ShopifyAPI::Utils::HmacValidator.validate` succeeds because it only checks `B` against `H` ( [5](#0-4) ).
5. `Registry.process` dispatches the handler with `shop: "victim.myshopify.com"` and the attacker's body content, even though the event never actually occurred for that shop ( [6](#0-5) ).

### Citations

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
