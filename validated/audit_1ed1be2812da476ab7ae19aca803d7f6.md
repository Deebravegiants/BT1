This confirms the finding: the gem's documented webhook API explicitly tells app developers to trust `data.shop` as "The shop domain of the webhook" for tenant identification (`docs/usage/webhooks.md:14`), yet the HMAC validation performed in `ShopifyAPI::Webhooks::Registry.process` only covers the request body, not the shop-domain header.### Title
Webhook `X-Shopify-Shop-Domain` tenant identifier is not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body. The `shop` value that the gem hands to the app's handler as the tenant identifier — and that the docs explicitly instruct developers to trust ("`shop`, `String` - The shop domain of the webhook") — comes from the `X-Shopify-Shop-Domain`/`shopify-shop-domain` header, which is never included in the signed bytes. Because the signing secret (`Context.api_secret_key`) is a single app-wide secret shared across every shop that installs the app (not a per-shop secret), any party who can obtain one valid `(raw_body, hmac)` pair for their own tenant can replay that exact pair against the app's public webhook endpoint while substituting a victim shop's domain in the header, and the check will still pass.

### Finding Description
- `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
- `shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cross-check against the signed bytes: [2](#0-1) 
- `Registry.process` validates only `Utils::HmacValidator.validate(request)` (which validates `to_signable_string`, i.e. body only) before building `WebhookMetadata` from `request.shop` and dispatching to the app's handler: [3](#0-2) 
- `HmacValidator.validate` computes `HMAC-SHA256(api_secret_key, verifiable_query.to_signable_string)` and compares it to the header HMAC — again, `shop` plays no role in the computed digest: [4](#0-3) 
- `api_secret_key` is a single, app-level secret (`ShopifyAPI::Context.api_secret_key`) used identically for every shop that installs the app — it is not shop-specific: [5](#0-4) 
- The documentation instructs developers that `data.shop` (i.e. `WebhookMetadata#shop`, sourced from `request.shop`) is "The shop domain of the webhook" and should be used to key work such as `perform_later(topic: data.topic, shop_domain: data.shop, ...)`, confirming this field is meant to be trusted as the tenant identity: [6](#0-5) 
- `WebhookMetadata` is a plain struct with no additional integrity guard on `shop`: [7](#0-6) 

Because the same `api_secret_key` signs webhooks for every shop that has the app installed, `HMAC-SHA256(secret, body)` is identical for identical bodies regardless of which shop the webhook is nominally "from." An attacker who legitimately installs the target app on their own (attacker-controlled) shop — which requires no privileged credentials, just a normal Shopify dev/trial store — can trigger or predict a webhook delivery for their own shop and thereby obtain a valid `(raw_body, hmac)` pair signed with the app's secret. They can then POST that same `raw_body` and `hmac` header to the app's public webhook endpoint while setting `X-Shopify-Shop-Domain` to an arbitrary victim shop's domain. `Registry.process` will validate the HMAC successfully (since it only checks the body) and deliver `WebhookMetadata` claiming the forged data belongs to the victim shop.

This is a direct analog of the reported bug class: a field (`shop`) that the app acts on for tenant identity is not covered by the cryptographic binding (`HMAC`) that is actually verified, breaking the equality `verified_bytes == acted_upon_identity`.

### Impact Explanation
This breaks tenant isolation: an attacker can cause the app's webhook handler to process attacker-chosen body content under an arbitrary victim shop's identity, since the shop is unauthenticated relative to the signature. Depending on how the host app uses `data.shop` (e.g., to look up/update per-shop records, queue background jobs keyed by shop, or trigger `app/uninstalled`-style side effects), this enables cross-tenant data injection/corruption attributed to a shop the attacker does not control — this is a cross-tenant access issue.

### Likelihood Explanation
Exploitability requires only: (1) the app's webhook endpoint being publicly reachable (true by design — it's an HTTP callback URL), and (2) the attacker being able to obtain one valid `(body, hmac)` pair, which they can get by installing the app on any shop they control (a free/trial Shopify store is trivially available to any internet user) and receiving a real webhook, or by relying on predictable/empty bodies (e.g., filtered fields or webhooks with minimal payloads) that are identical across shops. No access token, `client_secret`, or privileged account is required to mount the replay against a different, victim shop.

### Recommendation
Bind the `shop` domain (and ideally `topic`/`webhook_id`) into the signed material, or independently verify that the shop in the header actually owns an active webhook subscription/session before trusting `data.shop`. At minimum, document and/or enforce that `Registry.process` cross-validates the shop domain against a known/registered shop (e.g., a session store lookup) rather than passing the raw header value straight through to `WebhookMetadata`.

### Proof of Concept
1. Install the target app on an attacker-controlled test store `attacker-shop.myshopify.com`; trigger any subscribed webhook topic (or use a topic/fields configuration that yields a fixed/empty JSON body, e.g. `"{}"`).
2. Capture the delivered `raw_body` and its `X-Shopify-Hmac-Sha256` value — this is valid because it was computed with the app's shared `api_secret_key` over just the body, as shown in the test helper: [8](#0-7) 
3. Send a POST to the app's public webhook endpoint with the same `raw_body` and `X-Shopify-Hmac-Sha256`, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` passes (body/HMAC match), and `Registry.process` dispatches `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)` to the app's handler, which will treat the forged payload as legitimately originating from the victim shop.

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

**File:** lib/shopify_api/context.rb (L151-160)
```ruby
      sig { returns(T::Boolean) }
      def private?
        @is_private
      end

      sig { returns(T.nilable(String)) }
      attr_reader :private_shop, :user_agent_prefix, :old_api_secret_key, :host, :api_host

      sig { returns(T::Boolean) }
      attr_reader :expiring_offline_access_tokens
```

**File:** docs/usage/webhooks.md (L12-30)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
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

**File:** test/webhooks/registry_test.rb (L284-298)
```ruby
        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        new_format_headers = {
          "shopify-topic" => @topic,
          "shopify-hmac-sha256" => Base64.encode64(hmac),
          "shopify-shop-domain" => @shop,
          "shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "shopify-api-version" => "2024-01",
        }

        webhook_request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: new_format_headers)
```
