The report's bug class — an invariant that is checked in one place but never enforced where it is actually relied upon — maps directly onto how `ShopifyAPI::Webhooks::Request` computes and verifies its HMAC.

### Title
Webhook shop-domain (and topic/webhook-id) not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented as verifying "the request did indeed come from Shopify," but the HMAC it validates only binds the raw JSON body. The `shop-domain` header — which is the value actually used to attribute the incoming webhook event to a tenant — is never part of the signed data.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `to_signable_string` and compares it against the `hmac-sha256` header: [2](#0-1) 

`Registry.process` trusts `request.shop` (read straight from the `shop-domain` header) once the HMAC check passes, and hands it to the app's handler as the tenant identifier: [3](#0-2) 

The `shop` attribute is read from a header that is completely outside the signed payload: [4](#0-3) 

The invariant that should hold — "the shop attributed to a webhook event must be covered by the same HMAC that authenticates the event" — is never enforced. Because a single app-wide `client_secret` is used to sign webhooks for *every* installed shop, and because the webhook endpoint is one shared public route for all tenants (as shown in the gem's own docs, `docs/usage/webhooks.md:127-135`), any shop that has legitimately installed the app can capture one of its own genuine Shopify-signed webhook deliveries (raw body + `hmac-sha256` header) and replay that exact body/HMAC pair to the same public endpoint while substituting the `shop-domain` (and/or `topic`, `webhook-id`, `api-version`) header with another merchant's shop domain. `HmacValidator.validate` will still return `true`, since the signature never covered those headers, and `Registry.process` will invoke the handler with `data.shop` set to the victim's domain.

### Impact Explanation
This breaks the tenant boundary that `process` is documented to enforce: `shop_authenticated == shop_used_for_tenant_attribution` does not hold. An unprivileged Shopify merchant who has installed the target app can forge cross-tenant webhook events for *any other* merchant of the same app, e.g. spoofing `app/uninstalled`, `customers/data_request`, `orders/create`, etc. for a victim shop. Depending on what the host app does with `data.shop` (data writes, deletion cascades, compliance actions, cache invalidation, job dispatch keyed by shop), this enables cross-tenant data corruption/injection — matching the Critical "cross-tenant access" impact class.

### Likelihood Explanation
Exploitation only requires: (1) installing the target Shopify app in an attacker-controlled development/test store — something any unprivileged internet user can do for public apps — to obtain one authentic signed webhook, and (2) resending that captured `raw_body` + `hmac-sha256` value to the app's known public webhook URL with a different `shop-domain` header. No access to the app's `client_secret`, an access token, or any victim credentials is required.

### Recommendation
Include the authenticated tenant identity in the value that is HMAC-verified, or otherwise cryptographically bind the `shop-domain` (and `topic`/`webhook-id`) to the signature before trusting it — e.g., have `Registry.process`/`HmacValidator` reject any request unless the shop domain has been independently corroborated (such as looking up the topic/webhook-id via the Admin API for that specific shop's stored session, or requiring the host app to validate `request.shop` against a known/installed shop list before consuming the event). At minimum, update `docs/usage/webhooks.md` to explicitly warn that `Registry.process` only authenticates the request body, not the shop attribution, so implementers don't treat `data.shop` as HMAC-verified.

### Proof of Concept
```ruby
# Attacker installs the target app on their own shop "attacker.myshopify.com"
# and captures a genuine webhook delivery from Shopify:
raw_body = '{"id":1}'
real_hmac_header = "<value Shopify sent for attacker's own shop>"

# Attacker replays the identical body/HMAC pair but swaps the shop header
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => real_hmac_header,   # unchanged, still valid
  "x-shopify-shop-domain" => "victim.myshopify.com", # forged
  "x-shopify-webhook-id" => "forged-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (HMAC only covers raw_body),
#    handler.handle(data: WebhookMetadata.new(shop: "victim.myshopify.com", ...)) is invoked,
#    attributing attacker-controlled event data to the victim's tenant.
``` [3](#0-2) [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-43)
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
